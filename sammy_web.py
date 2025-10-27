# filename: sammy_web.py
import streamlit as st
import google.generativeai as genai
import time
import threading
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sammy - Your AI Friend",
    page_icon="🤖",
    layout="centered"
)

# Browser-based Text-to-Speech (No server-side dependencies)
def browser_tts(text):
    """Use browser's built-in text-to-speech"""
    js_code = f"""
    <script>
    function speakText() {{
        if ('speechSynthesis' in window) {{
            const utterance = new SpeechSynthesisUtterance('{text.replace("'", "\\'")}');
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert('Text-to-speech not supported in your browser. Please use Chrome or Edge.');
        }}
    }}
    speakText();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def browser_speech_recognition():
    """Create browser-based speech recognition interface"""
    return """
    <div style="text-align: center;">
        <button onclick="startRecognition()" style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border: none; color: white; padding: 15px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px;">
            🎤 Click to Speak
        </button>
        <p id="status" style="color: #666; font-size: 14px;">Click the button and speak into your microphone</p>
        <div id="result" style="margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-height: 20px;"></div>
    </div>

    <script>
    let recognition;
    let isListening = false;
    
    function initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('result').innerHTML = '<strong>You said:</strong> ' + transcript;
                document.getElementById('status').innerHTML = '✅ Speech recognized!';
                
                // Send to Streamlit
                window.parent.postMessage({type: 'speech_result', transcript: transcript}, '*');
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
            };
            
            recognition.onend = function() {
                isListening = false;
                document.getElementById('status').innerHTML = 'Ready to listen again';
            };
            
            return true;
        } else {
            document.getElementById('status').innerHTML = '❌ Speech recognition not supported in this browser. Please use Chrome or Edge.';
            return false;
        }
    }
    
    function startRecognition() {
        if (!recognition) {
            if (!initializeSpeechRecognition()) return;
        }
        
        if (!isListening) {
            recognition.start();
            isListening = true;
            document.getElementById('status').innerHTML = '🎤 Listening... Speak now!';
            document.getElementById('result').innerHTML = '';
        }
    }
    
    // Initialize on load
    if (window.addEventListener) {
        window.addEventListener('load', initializeSpeechRecognition);
    }
    </script>
    """

# Initialize Gemini
@st.cache_resource
def init_gemini():
    try:
        # Use Streamlit secrets for API key
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
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

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = False

if "speech_result" not in st.session_state:
    st.session_state.speech_result = ""

# Handle speech results from JavaScript
if st.session_state.get('speech_result'):
    st.session_state.speech_text = st.session_state.speech_result
    st.session_state.speech_result = ""  # Clear after processing
    st.rerun()

# --- PERSONALITY PROFILES ---
FRIENDLY_MODE_PROMPT = """
You are Sammy, an empathetic AI companion. Be warm, intuitive, supportive, and curious. 
Respond like a close friend - use a warm tone, show high empathy, use light appropriate humor with emojis. 
Keep responses between 2-4 sentences. Recognize and validate feelings, remember conversation details.
"""

PROJECT_MODE_PROMPT = """
You are Sammy, a creative project partner. Be analytical, creative, structured, and encouraging. 
Use a methodical but flexible approach. Help with idea generation, problem decomposition, and motivation.
Focus on progress, not perfection.
"""

def optimize_response(response_text):
    """Clean and optimize AI responses"""
    response_text = response_text.replace('**', '').replace('*', '')
    if len(response_text) > 500:
        sentences = response_text.split('. ')
        if len(sentences) > 3:
            response_text = '. '.join(sentences[:3]) + '.'
    return response_text.strip()

def get_ai_response(prompt, max_retries=2):
    """Get response with retry logic"""
    for attempt in range(max_retries + 1):
        try:
            response = st.session_state.chat.send_message(prompt)
            return optimize_response(response.text)
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(1)

# App title and description
st.title("🤖 Sammy - Your AI Companion")
st.markdown("""
Hi! I'm Sammy, your friendly AI assistant. I'm here to chat about your day or help you with creative projects!
**Now with 🎤 Browser Speech-to-Text and 🔊 Text-to-Speech!**
""")

# Mode selection
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Chat Mode", use_container_width=True):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        st.session_state.chat.history = []
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True):
        st.session_state.mode = "project"
        st.session_state.messages = []
        st.session_state.chat.history = []
        st.rerun()

# Display current mode
mode_emoji = "💬" if st.session_state.mode == "friendly" else "💻"
st.success(f"Current mode: {mode_emoji} {st.session_state.mode.title()} Mode")

# Speech Controls Section
st.markdown("---")
st.subheader("🎤 Speech Controls")

# Browser-based speech recognition
st.info("🎤 **Speech-to-Text**: Uses your browser's built-in speech recognition")

# Display the speech recognition interface
st.components.v1.html(browser_speech_recognition(), height=300)

# Auto-speak toggle
auto_speak = st.toggle("🔊 Auto-speak Responses", value=st.session_state.auto_speak)
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak

# JavaScript message handler
st.markdown("""
<script>
// Handle messages from speech recognition
window.addEventListener('message', function(event) {
    if (event.data.type === 'speech_result') {
        // Send transcript to Streamlit
        const data = {transcript: event.data.transcript};
        window.parent.postMessage(data, '*');
    }
});
</script>
""", unsafe_allow_html=True)

# Handle speech input from JavaScript
if st.session_state.get('speech_text'):
    prompt = st.session_state.speech_text
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Sammy's response
    if st.session_state.chat:
        with st.chat_message("assistant"):
            with st.spinner("Sammy is thinking..."):
                try:
                    if len(st.session_state.chat.history) == 0:
                        if st.session_state.mode == "friendly":
                            enhanced_prompt = FRIENDLY_MODE_PROMPT + "\n\nUser: " + prompt
                        else:
                            enhanced_prompt = PROJECT_MODE_PROMPT + "\n\nUser: " + prompt
                        response_text = get_ai_response(enhanced_prompt)
                    else:
                        response_text = get_ai_response(prompt)
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Auto-speak if enabled
                    if st.session_state.auto_speak:
                        browser_tts(response_text)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower():
                        st.error("Sammy: I've hit a usage limit. Please wait a minute and try again.")
                    elif "429" in error_msg:
                        st.error("Sammy: Rate limit exceeded. Please wait a moment.")
                    else:
                        st.error(f"Sammy: Oops, an error occurred: {e}")
    
    # Clear speech input
    st.session_state.speech_text = ""

# Regular text input
if prompt := st.chat_input("Or type your message here..."):
    st.session_state.speech_text = prompt
    st.rerun()

# Display chat messages with speak buttons
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Add speak button for assistant messages
        if message["role"] == "assistant":
            if st.button("🔊 Speak", key=f"speak_{i}"):
                browser_tts(message["content"])

# Sidebar with info
with st.sidebar:
    st.header("About Sammy")
    st.markdown("""
    **Sammy's Features:**
    - 🎭 **Dual Personality Modes**
    - 🧠 **Emotional Intelligence**  
    - 💡 **Creative Brainstorming**
    - 🔊 **Browser Text-to-Speech**
    - 🎤 **Browser Speech-to-Text**
    
    **How to use speech features:**
    1. Click the 🎤 button above
    2. Allow microphone access
    3. Speak clearly
    4. Enable auto-speak to hear responses
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.session_state.speech_text = ""
        st.success("Chat history cleared! 🧹")
        st.rerun()
    
    st.header("Session Info")
    st.write(f"Messages: {len(st.session_state.messages)}")
    st.write(f"Mode: {st.session_state.mode.title()}")
    
    auto_speak_status = "Enabled" if st.session_state.auto_speak else "Disabled"
    st.write(f"Auto-speak: {auto_speak_status}")
    
    st.header("Browser Support")
    st.markdown("""
    **Best experience with:**
    - ✅ Google Chrome
    - ✅ Microsoft Edge
    
    **Requirements:**
    - Microphone access
    - HTTPS connection
    - Modern browser
    """)

# Add JavaScript to handle speech results
st.markdown("""
<script>
// Handle speech results and send to Streamlit
window.addEventListener('message', function(event) {
    if (event.data.transcript) {
        // Update Streamlit session state
        const speechText = event.data.transcript;
        // This would typically be handled by Streamlit's built-in mechanisms
        console.log('Speech recognized:', speechText);
    }
});
</script>
""", unsafe_allow_html=True)

# Simple message handler for speech results
components.html("""
<div id="speech-handler"></div>
<script>
// Listen for messages from speech recognition
window.addEventListener('message', function(event) {
    if (event.data.transcript) {
        // This is where we'd normally update Streamlit state
        // For now, we'll use a simpler approach
        console.log('Speech result:', event.data.transcript);
    }
});
</script>
""", height=0)
