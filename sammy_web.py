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

# Browser-based Text-to-Speech
def browser_tts(text):
    """Use browser's built-in text-to-speech"""
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
            console.log('TTS not supported');
        }}
    }}
    speakText();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# Initialize Gemini
@st.cache_resource
def init_gemini():
    try:
        # Try to get API key from secrets
        api_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("🔑 API Key not found. Please add GOOGLE_API_KEY to Streamlit secrets.")
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

if "speech_input" not in st.session_state:
    st.session_state.speech_input = ""

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
**Now with 🎤 Speech-to-Text and 🔊 Text-to-Speech!**
""")

# Show API key status
if not st.session_state.model:
    st.warning("""
    **API Key Setup Required:**
    1. Go to your app on Streamlit Cloud
    2. Click Settings → Secrets
    3. Add your Google API key:
    ```toml
    GOOGLE_API_KEY = "your_api_key_here"
    ```
    """)

# Simple speech recognition using Streamlit's form
st.markdown("---")
st.subheader("🎤 Speech Input")

# Method 1: Simple text input that can be filled by speech
speech_text = st.text_area("Your message (use speech or type):", 
                          key="speech_input", 
                          height=100,
                          placeholder="Click the speech button below and speak, or type your message here...")

# Speech recognition button with JavaScript
speech_js = """
<div style="text-align: center; margin: 20px 0;">
    <button onclick="startSpeechRecognition()" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer;">
        🎤 Click to Speak
    </button>
    <p id="status" style="color: #666; margin-top: 10px;">Click the button and allow microphone access</p>
</div>

<script>
function startSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Use Chrome or Edge.';
        return;
    }
    
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = function() {
        document.getElementById('status').innerHTML = '🎤 Listening... Speak now!';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('status').innerHTML = '✅ Speech recognized: ' + transcript;
        
        // Create a form to submit the transcript back to Streamlit
        const form = document.createElement('form');
        form.method = 'post';
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'speech_result';
        input.value = transcript;
        form.appendChild(input);
        document.body.appendChild(form);
        
        // Use Streamlit's built-in form submission
        const streamlitDoc = window.parent.document;
        const streamlitForm = streamlitDoc.querySelector('form');
        if (streamlitForm) {
            const textArea = streamlitForm.querySelector('textarea');
            if (textArea) {
                textArea.value = transcript;
                // Trigger form submission
                streamlitForm.dispatchEvent(new Event('submit', {bubbles: true}));
            }
        }
    };
    
    recognition.onerror = function(event) {
        document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
    };
    
    recognition.onend = function() {
        document.getElementById('status').innerHTML = 'Ready to listen again';
    };
    
    recognition.start();
}
</script>
"""

st.components.v1.html(speech_js, height=150)

# Alternative: Manual speech input method
st.markdown("### Alternative Method")
st.info("""
**If the button above doesn't work:**
1. **Type your message** in the text area above
2. **OR use your device's built-in speech-to-text:**
   - **Windows:** Press `Win + H` 
   - **Mac:** Press `Fn key twice`
   - **Mobile:** Use your keyboard's microphone button
""")

# Auto-speak toggle
auto_speak = st.toggle("🔊 Auto-speak Responses", value=st.session_state.auto_speak)
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak

# Send button
if st.button("📤 Send Message", type="primary", use_container_width=True):
    if speech_text.strip():
        st.session_state.process_input = speech_text

# Also process chat input
if prompt := st.chat_input("Or chat here..."):
    st.session_state.process_input = prompt

# Process the input
if st.session_state.get('process_input'):
    prompt = st.session_state.process_input
    del st.session_state.process_input
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Sammy's response
    if st.session_state.chat and st.session_state.model:
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
    else:
        st.error("Sammy is not properly initialized. Please check your API key.")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Add speak button for assistant messages
        if message["role"] == "assistant":
            if st.button("🔊 Speak", key=f"speak_{i}"):
                browser_tts(message["content"])

# Mode selection
st.markdown("---")
st.subheader("Chat Mode")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Chat Mode", use_container_width=True):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True):
        st.session_state.mode = "project"
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()

# Display current mode
mode_emoji = "💬" if st.session_state.mode == "friendly" else "💻"
st.success(f"Current mode: {mode_emoji} {st.session_state.mode.title()} Mode")

# Sidebar
with st.sidebar:
    st.header("About Sammy")
    st.markdown("""
    **How to use speech features:**
    1. **Click the 🎤 button**
    2. **Allow microphone access** when browser asks
    3. **Speak clearly** into your microphone
    4. **Your speech will appear** in the text area
    5. **Click "Send Message"** to send it to Sammy
    
    **Browser requirements:**
    - ✅ Google Chrome (recommended)
    - ✅ Microsoft Edge
    - ❌ May not work on Safari/Firefox
    - Requires microphone permission
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.session_state.speech_input = ""
        st.success("Chat history cleared!")
        st.rerun()
    
    st.header("Session Info")
    st.write(f"Messages: {len(st.session_state.messages)}")
    st.write(f"Mode: {st.session_state.mode.title()}")
    st.write(f"Auto-speak: {'On' if st.session_state.auto_speak else 'Off'}")

# Instructions for speech recognition
st.markdown("---")
st.info("""
**💡 Tip:** If speech recognition doesn't work:
1. **Use Chrome or Edge browser**
2. **Allow microphone access** when prompted
3. **Speak clearly** and not too fast
4. **Alternatively, use your device's built-in dictation** (Windows: Win+H, Mac: Fn key twice)
""")
