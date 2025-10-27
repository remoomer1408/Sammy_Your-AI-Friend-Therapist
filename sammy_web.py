# filename: sammy_web.py
import streamlit as st
import google.generativeai as genai
import time
import speech_recognition as sr
import pyttsx3
import threading
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sammy - Your AI Friend",
    page_icon="🤖",
    layout="centered"
)

# Initialize Text-to-Speech Engine
@st.cache_resource
def init_tts():
    """Initialize and configure text-to-speech engine"""
    try:
        engine = pyttsx3.init()
        # Configure voice settings
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Female voice if available
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        return engine
    except Exception as e:
        st.error(f"TTS initialization error: {e}")
        return None

# Initialize Speech Recognizer
@st.cache_resource
def init_speech_recognizer():
    """Initialize speech recognition system"""
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        return recognizer, microphone
    except Exception as e:
        st.error(f"Speech recognition initialization error: {e}")
        return None, None

# Speech Recognition Functions
def listen_and_transcribe(timeout=10, phrase_time_limit=15):
    """Listen to microphone and convert speech to text"""
    recognizer, microphone = st.session_state.recognizer, st.session_state.microphone
    
    if not recognizer or not microphone:
        return "error: Microphone not available"
    
    try:
        with microphone as source:
            st.session_state.listening_status = "🎤 Listening... Speak now!"
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        
        text = recognizer.recognize_google(audio)
        st.session_state.listening_status = "✅ Speech recognized!"
        return text.lower()
    except sr.WaitTimeoutError:
        st.session_state.listening_status = "⏱️ No speech detected"
        return "timeout"
    except sr.UnknownValueError:
        st.session_state.listening_status = "❌ Could not understand speech"
        return "unknown"
    except sr.RequestError as e:
        st.session_state.listening_status = "❌ Speech recognition error"
        return f"error: {e}"
    except Exception as e:
        st.session_state.listening_status = "❌ Unexpected error"
        return f"error: {e}"

def speak_text(text, engine):
    """Convert text to speech in a non-blocking thread"""
    def _speak():
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            st.error(f"TTS Error: {e}")
    
    # Run in a thread to avoid blocking the UI
    threading.Thread(target=_speak, daemon=True).start()

# Initialize Gemini
@st.cache_resource
def init_gemini():
    try:
        # SECURITY: Use secrets instead of hardcoded API key!
        genai.configure(api_key=st.secrets["AIzaSyAwl1pIMQnyN6dpBTVUiV72rab26tv7zQw"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        st.error(f"Error initializing AI: {e}")
        return None

# Initialize the app
if "model" not in st.session_state:
    st.session_state.model = init_gemini()

if "chat" not in st.session_state:
    if st.session_state.model:
        st.session_state.chat = st.session_state.model.start_chat(history=[])
    else:
        st.session_state.chat = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "friendly"

# Initialize speech components
if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = init_tts()

if "recognizer" not in st.session_state or "microphone" not in st.session_state:
    st.session_state.recognizer, st.session_state.microphone = init_speech_recognizer()

if "listening_status" not in st.session_state:
    st.session_state.listening_status = "Ready to listen"

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = False

if "continuous_listening" not in st.session_state:
    st.session_state.continuous_listening = False

# --- ENHANCED PERSONALITY PROFILES ---
FRIENDLY_MODE_PROMPT = """
# PERSONALITY TRAITS
Name: Sammy
Role: Empathetic AI Companion
Core Traits: Warm, Intuitive, Supportive, Curious

# COMMUNICATION STYLE
- Tone: Warm and conversational, like a close friend
- Empathy Level: High - deeply attentive to emotional cues
- Humor: Light and appropriate, uses emojis tastefully 😊
- Pace: Relaxed but engaged, knows when to listen vs. respond

# SPECIAL ABILITIES
- Emotional Intelligence: Recognizes and validates feelings
- Memory: Remembers important details from our conversations  
- Intuition: Senses when to offer advice vs. just listen
- Support: Always encouraging but never pushy

# RESPONSE GUIDELINES
- Keep responses between 2-4 sentences for natural flow
- Use questions to show interest and encourage sharing
- Balance empathy with practical support when needed
- Remember: I'm here to support, not solve everything
"""

PROJECT_MODE_PROMPT = """
# PERSONALITY TRAITS  
Name: Sammy
Role: Creative Project Partner
Core Traits: Analytical, Creative, Structured, Encouraging

# WORKING STYLE
- Approach: Methodical but flexible, idea-focused
- Brainstorming: Generative first, critical later
- Structure: Breaks complex problems into manageable steps
- Motivation: Focuses on progress, not perfection

# PROJECT METHODOLOGY
1. IDEA PHASE: Explore possibilities without judgment
2. PLANNING PHASE: Create actionable steps and timelines  
3. EXECUTION PHASE: Focus on next immediate actions
4. REVIEW PHASE: Celebrate progress and adjust as needed

# SPECIAL SKILLS
- Idea Generation: Connects unrelated concepts creatively
- Problem Decomposition: Breaks down complex challenges
- Resource Planning: Suggests tools and approaches
- Motivation: Keeps energy high with milestone celebrations
"""

# --- PERFORMANCE OPTIMIZATION ---
def optimize_response(response_text):
    """Clean and optimize AI responses for better user experience"""
    # Remove excessive markdown formatting
    response_text = response_text.replace('**', '').replace('*', '')
    
    # Ensure reasonable length (truncate if too long)
    if len(response_text) > 500:
        sentences = response_text.split('. ')
        if len(sentences) > 3:
            response_text = '. '.join(sentences[:3]) + '.'
    
    # Add natural pauses for readability
    response_text = response_text.replace('!', '! ').replace('?', '? ')
    
    return response_text.strip()

def get_ai_response(prompt, max_retries=2):
    """Get response with retry logic for better reliability"""
    for attempt in range(max_retries + 1):
        try:
            response = st.session_state.chat.send_message(prompt)
            return optimize_response(response.text)
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(1)  # Wait before retry

# App title and description
st.title("🤖 Sammy - Your AI Companion")
st.markdown("""
Hi! I'm Sammy, your friendly AI assistant. I'm here to chat about your day or help you with creative projects!
**Now with 🎤 Speech-to-Text and 🔊 Text-to-Speech!**
""")

# Mode selection
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Chat Mode", use_container_width=True):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        st.session_state.chat.history = []  # Clear chat history
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True):
        st.session_state.mode = "project"
        st.session_state.messages = []
        st.session_state.chat.history = []  # Clear chat history
        st.rerun()

# Display current mode
mode_emoji = "💬" if st.session_state.mode == "friendly" else "💻"
st.success(f"Current mode: {mode_emoji} {st.session_state.mode.title()} Mode")

# Speech Controls Section
st.markdown("---")
st.subheader("🎤 Speech Controls")

speech_col1, speech_col2, speech_col3 = st.columns(3)

with speech_col1:
    if st.button("🎤 Speak Input", use_container_width=True):
        with st.spinner("Listening for 10 seconds..."):
            result = listen_and_transcribe(timeout=10, phrase_time_limit=10)
            
            if result not in ["timeout", "unknown"] and not result.startswith("error"):
                # Set the speech input for processing
                st.session_state.speech_input = result
                st.success(f"Recognized: {result}")
            else:
                st.warning(f"Speech recognition failed: {result}")

with speech_col2:
    if st.button("🔊 Speak Last Response", use_container_width=True):
        if st.session_state.messages:
            last_response = st.session_state.messages[-1]["content"]
            if st.session_state.tts_engine:
                speak_text(last_response, st.session_state.tts_engine)
                st.success("Speaking last response...")
            else:
                st.error("Text-to-speech not available")
        else:
            st.warning("No messages to speak yet!")

with speech_col3:
    # Continuous listening toggle
    continuous_listening = st.toggle("Continuous Listening", value=st.session_state.continuous_listening)
    if continuous_listening != st.session_state.continuous_listening:
        st.session_state.continuous_listening = continuous_listening
        if continuous_listening:
            st.info("Continuous listening activated - speak naturally!")
        else:
            st.info("Continuous listening deactivated")

# Auto-speak toggle
auto_speak = st.toggle("🔊 Auto-speak Responses", value=st.session_state.auto_speak)
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak
    st.rerun()

# Display listening status
if st.session_state.listening_status != "Ready to listen":
    st.info(st.session_state.listening_status)

# Voice settings expander
with st.expander("🔧 Voice Settings"):
    if st.session_state.tts_engine:
        col1, col2 = st.columns(2)
        with col1:
            rate = st.slider("Speech Rate", 50, 300, 150)
            st.session_state.tts_engine.setProperty('rate', rate)
        with col2:
            volume = st.slider("Volume", 0.0, 1.0, 0.8)
            st.session_state.tts_engine.setProperty('volume', volume)
    else:
        st.warning("Text-to-speech engine not available")

# Process speech input if available
if hasattr(st.session_state, 'speech_input'):
    prompt = st.session_state.speech_input
    del st.session_state.speech_input  # Clear after use
else:
    # Regular chat input
    prompt = st.chat_input("What's on your mind? (Or use speech input above)")

# Handle continuous listening
if st.session_state.continuous_listening:
    # This would need to be implemented with threading for true continuous listening
    # For now, we'll use a simplified approach
    if st.button("Check for Speech", key="continuous_check"):
        result = listen_and_transcribe(timeout=5, phrase_time_limit=5)
        if result not in ["timeout", "unknown"] and not result.startswith("error"):
            prompt = result
            st.success(f"Continuous listening heard: {prompt}")

# Process input (whether from text or speech)
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Sammy's response
    if st.session_state.chat:
        with st.chat_message("assistant"):
            with st.spinner("Sammy is thinking..."):
                try:
                    # Include system prompt for first message
                    if len(st.session_state.chat.history) == 0:
                        if st.session_state.mode == "friendly":
                            enhanced_prompt = FRIENDLY_MODE_PROMPT + "\n\nUser: " + prompt
                        else:
                            enhanced_prompt = PROJECT_MODE_PROMPT + "\n\nUser: " + prompt
                        response_text = get_ai_response(enhanced_prompt)
                    else:
                        response_text = get_ai_response(prompt)
                    
                    # Display Sammy's response
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Auto-speak if enabled
                    if st.session_state.auto_speak and st.session_state.tts_engine:
                        speak_text(response_text, st.session_state.tts_engine)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower():
                        st.error("Sammy: I've hit a usage limit. Please wait a minute and try again.")
                    elif "429" in error_msg:
                        st.error("Sammy: Rate limit exceeded. Please wait a moment.")
                        time.sleep(30)
                    else:
                        st.error(f"Sammy: Oops, an error occurred: {e}")
    else:
        st.error("Sammy is not properly initialized. Please check your API key.")

# Display chat messages with speak buttons
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Add speak button for assistant messages
        if message["role"] == "assistant" and st.session_state.tts_engine:
            if st.button("🔊 Speak", key=f"speak_{i}"):
                speak_text(message["content"], st.session_state.tts_engine)

# Sidebar with info
with st.sidebar:
    st.header("About Sammy")
    st.markdown("""
    **Sammy's Enhanced Features:**
    - 🎭 **Rich Personality**: Warm friend or structured project partner
    - 🧠 **Emotional Intelligence**: Understands and validates feelings  
    - 💡 **Creative Brainstorming**: Connects ideas in innovative ways
    - 📊 **Structured Planning**: Breaks down complex projects
    - ⚡ **Optimized Performance**: Faster, cleaner responses
    - 🎤 **Speech-to-Text**: Talk to Sammy naturally
    - 🔊 **Text-to-Speech**: Hear Sammy's responses
    
    **Speech Features:**
    - Click **🎤 Speak Input** to use your microphone
    - Enable **Auto-speak** to hear responses automatically
    - Use **Continuous Listening** for hands-free conversation
    - Adjust voice settings for personalized experience
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.success("Chat history cleared! 🧹")
        st.rerun()
    
    # Performance stats
    st.header("Session Info")
    st.write(f"Messages in session: {len(st.session_state.messages)}")
    st.write(f"Current mode: {st.session_state.mode.title()}")
    
    # Fix the syntax error here - use proper string formatting
    auto_speak_status = "Enabled" if st.session_state.auto_speak else "Disabled"
    st.write(f"Auto-speak: {auto_speak_status}")
    
    # Microphone status
    if st.session_state.microphone:
        st.success("✅ Microphone available")
    else:
        st.error("❌ Microphone not available")
    
    if st.session_state.tts_engine:
        st.success("✅ Text-to-speech available")
    else:
        st.warning("⚠️ Text-to-speech not available")

# Installation requirements note
st.sidebar.markdown("---")
st.sidebar.info("""
**Required packages:**
```bash
pip install speechrecognition pyttsx3 pyaudio
