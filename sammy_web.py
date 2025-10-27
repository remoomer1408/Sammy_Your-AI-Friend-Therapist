# filename: sammy_web.py
import streamlit as st
import google.generativeai as genai
import time

# Page configuration
st.set_page_config(
    page_title="Sammy - Your AI Friend",
    page_icon="🤖",
    layout="centered"
)

# Browser-based Text-to-Speech (No server-side dependencies)
def browser_tts(text):
    """Use browser's built-in text-to-speech"""
    # Clean text for JavaScript
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    js_code = f"""
    <script>
    function speakText() {{
        if ('speechSynthesis' in window) {{
            const utterance = new SpeechSynthesisUtterance('{clean_text}');
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            window.speechSynthesis.speak(utterance);
        }} else {{
            console.log('Text-to-speech not supported in your browser.');
        }}
    }}
    speakText();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def browser_speech_recognition():
    """Create browser-based speech recognition interface"""
    return """
    <div style="text-align: center; padding: 20px;">
        <button onclick="startRecognition()" style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border: none; color: white; padding: 15px 30px; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px;">
            🎤 Click to Speak
        </button>
        <p id="status" style="color: #666; font-size: 14px;">Click the button and speak into your microphone</p>
        <div id="result" style="margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-height: 20px; background: #f9f9f9;"></div>
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
                
                // Create a form to submit to Streamlit
                const form = document.createElement('form');
                form.method = 'POST';
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'speech_text';
                input.value = transcript;
                form.appendChild(input);
                document.body.appendChild(form);
                
                // Submit the form
                form.submit();
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
                document.getElementById('result').innerHTML = 'Please try again or use text input.';
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
    window.addEventListener('load', initializeSpeechRecognition);
    </script>
    """

# Initialize Gemini with proper error handling
@st.cache_resource
def init_gemini():
    try:
        # Try multiple ways to get the API key
        api_key = None
        
        # Method 1: Streamlit secrets
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            pass
        
        # Method 2: Try alternative secret name
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except:
                pass
        
        # Method 3: Try environment variable as fallback
        if not api_key:
            import os
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("🔑 API Key not found. Please add your Google API key to Streamlit secrets.")
            return None
            
        genai.configure(api_key=api_key)
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

# Handle form submissions for speech input
if st.session_state.get('speech_text'):
    prompt = st.session_state.speech_text
else:
    prompt = None

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

# Show API key status
if not st.session_state.model:
    st.warning("""
    **API Key Setup Required:**
    1. Go to [Streamlit Cloud](https://share.streamlit.io/)
    2. Click on your app → Settings (⋮) → Secrets
    3. Add your Google API key:
    ```toml
    GOOGLE_API_KEY = "your_actual_api_key_here"
    ```
    4. Redeploy the app
    """)

# Mode selection (only show if AI is initialized)
if st.session_state.model:
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
    st.info("🎤 **Speech-to-Text**: Uses your browser's built-in speech recognition (Chrome/Edge recommended)")

    # Display the speech recognition interface
    st.components.v1.html(browser_speech_recognition(), height=250)

    # Auto-speak toggle
    auto_speak = st.toggle("🔊 Auto-speak Responses", value=st.session_state.auto_speak)
    if auto_speak != st.session_state.auto_speak:
        st.session_state.auto_speak = auto_speak

    # Handle speech input
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Sammy's response
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
    if text_prompt := st.chat_input("Or type your message here..."):
        st.session_state.speech_text = text_prompt
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
        if 'speech_text' in st.session_state:
            st.session_state.speech_text = ""
        st.success("Chat history cleared! 🧹")
        st.rerun()
    
    st.header("Session Info")
    st.write(f"Messages: {len(st.session_state.messages)}")
    if st.session_state.model:
        st.write(f"Mode: {st.session_state.mode.title()}")
        
        auto_speak_status = "Enabled" if st.session_state.auto_speak else "Disabled"
        st.write(f"Auto-speak: {auto_speak_status}")
    else:
        st.write("Status: ❌ API Key Needed")
    
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

# Simple JavaScript for speech handling
st.markdown("""
<script>
// Handle speech results
window.addEventListener('message', function(event) {
    if (event.data.type === 'speech_result') {
        console.log('Speech result received');
    }
});
</script>
""", unsafe_allow_html=True)
