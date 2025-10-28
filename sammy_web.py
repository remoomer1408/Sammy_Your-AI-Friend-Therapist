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

# Improved browser TTS function
def speak_text(text):
    """Use browser's text-to-speech"""
    # Clean the text for JavaScript
    import re
    clean_text = re.sub(r'[^\w\s\.\?\!,]', '', text)  # Remove special characters
    clean_text = clean_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    
    js_code = f"""
    <script>
    function speak() {{
        if ('speechSynthesis' in window) {{
            // Stop any current speech
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance('{clean_text}');
            utterance.rate = 0.8;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            utterance.lang = 'en-US';
            
            window.speechSynthesis.speak(utterance);
        }}
    }}
    // Execute after a short delay
    setTimeout(speak, 100);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# Initialize Gemini with correct model names
@st.cache_resource
def init_gemini():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("❌ API Key not found. Add GOOGLE_API_KEY to Streamlit secrets.")
            return None
            
        genai.configure(api_key=api_key)
        
        # Try different model names - these are the most common ones
        model_attempts = [
            'gemini-1.5-flash',  # Most common new model
            'gemini-1.5-pro',    # Another common new model
            'gemini-1.0-pro',    # Older but stable
            'gemini-pro',        # Original name (might not work)
        ]
        
        for model_name in model_attempts:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                test_response = model.generate_content("Hello")
                st.success(f"✅ Using model: {model_name}")
                return model
            except Exception as e:
                st.sidebar.info(f"❌ {model_name} not available: {str(e)[:50]}...")
                continue
        
        # If no model works, show error
        st.error("❌ No working Gemini model found. Please check your API key and model availability.")
        return None
        
    except Exception as e:
        st.error(f"Error initializing AI: {e}")
        return None

# Initialize app state
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

# Fallback responses if AI fails
FALLBACK_RESPONSES = [
    "I'd love to chat with you, but there seems to be an issue with my AI capabilities. Please check your API key settings!",
    "Hello! I'm having trouble accessing my AI features at the moment. Could you verify your API key is correctly set up?",
    "I'm here to help, but I need a proper API key to function. Please check your Streamlit secrets configuration.",
    "Thanks for reaching out! There appears to be a configuration issue. Make sure your Google API key is properly set up."
]

# Personality prompts
FRIENDLY_PROMPT = """You are Sammy, a warm, empathetic AI friend. Be supportive, curious, and understanding. 
Respond in a conversational, friendly tone. Keep responses under 3 sentences when possible."""

PROJECT_PROMPT = """You are Sammy, a creative project partner. Be analytical, structured, and encouraging. 
Help break down complex tasks and provide practical advice."""

def get_ai_response(prompt):
    """Get response from Gemini with fallback"""
    if not st.session_state.model:
        # Return fallback response if model isn't available
        return FALLBACK_RESPONSES[len(st.session_state.messages) % len(FALLBACK_RESPONSES)]
    
    try:
        response = st.session_state.chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please check your API configuration."

# Main app
st.title("🤖 Sammy - Your AI Companion")
st.markdown("Chat with your AI friend! **Now with Text-to-Speech!**")

# Show API status
if not st.session_state.model:
    st.error("""
    **🔧 Setup Required:**
    1. Go to your Streamlit app settings
    2. Click on **Secrets**
    3. Add your Google API key:
    ```toml
    GOOGLE_API_KEY = "your_actual_api_key_here"
    ```
    4. Redeploy the app
    """)

# Mode selection (only show if model might work)
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Mode", use_container_width=True, key="btn_friendly"):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True, key="btn_project"):
        st.session_state.mode = "project"
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()

if st.session_state.model:
    st.success(f"Mode: {'💬 Friendly' if st.session_state.mode == 'friendly' else '💻 Project'}")
else:
    st.warning("AI model not initialized - using fallback responses")

# Text Input Section
st.markdown("---")
st.subheader("💬 Chat with Sammy")

user_input = st.text_area("Type your message to Sammy:", height=100, key="user_input", 
                         placeholder="What's on your mind? Type here...")

# Send button
if st.button("📤 Send Message", type="primary", use_container_width=True, key="btn_send"):
    if user_input.strip():
        st.session_state.process_input = user_input.strip()

# Also handle chat input
if chat_input := st.chat_input("Or type a quick message here..."):
    st.session_state.process_input = chat_input

# Process the message
if st.session_state.get('process_input'):
    prompt = st.session_state.process_input
    del st.session_state.process_input
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response (AI or fallback)
    with st.spinner("Sammy is thinking..."):
        if st.session_state.model:
            system_prompt = FRIENDLY_PROMPT if st.session_state.mode == "friendly" else PROJECT_PROMPT
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            response = get_ai_response(full_prompt)
        else:
            response = get_ai_response(prompt)  # This will use fallback
        
        # Add response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Auto-speak if enabled
        if st.session_state.auto_speak:
            time.sleep(0.5)
            speak_text(response)
    
    st.rerun()

# Text-to-Speech Controls
st.markdown("---")
st.subheader("🔊 Text-to-Speech")

# Auto-speak toggle
auto_speak = st.toggle("Automatically speak responses", 
                      value=st.session_state.auto_speak,
                      key="toggle_auto_speak")
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak

# Test TTS button
if st.button("🔊 Test Text-to-Speech", key="btn_test_tts"):
    test_text = "Hello! This is Sammy's text-to-speech test. If you can hear this, it's working!"
    speak_text(test_text)
    st.success("Testing text-to-speech... You should hear a message.")

# Display conversation
st.markdown("---")
st.subheader("📝 Conversation")

if not st.session_state.messages:
    st.info("No messages yet. Start a conversation above!")
else:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"**Sammy:** {message['content']}")
            with col2:
                if st.button("🔊", key=f"speak_{i}"):
                    speak_text(message["content"])

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear"):
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()
    
    st.header("📊 Session Info")
    st.write(f"**Messages:** {len(st.session_state.messages)}")
    st.write(f"**Mode:** {st.session_state.mode.title()}")
    st.write(f"**Auto-speak:** {'✅ On' if st.session_state.auto_speak else '❌ Off'}")
    st.write(f"**AI Status:** {'✅ Ready' if st.session_state.model else '❌ Needs Setup'}")
    
    st.header("🔑 API Setup")
    st.markdown("""
    **If AI isn't working:**
    1. Get a Google AI API key
    2. Add to Streamlit Secrets:
    ```toml
    GOOGLE_API_KEY = "your_key_here"
    ```
    3. Redeploy the app
    """)

# Instructions
st.markdown("---")
st.info("""
**💡 Troubleshooting Guide:**

**If you see model errors:**
- Check your Google AI API key is valid
- Ensure you have access to Gemini models
- Try redeploying the app

**If text-to-speech doesn't work:**
- Use **Chrome** or **Edge** browser
- Allow **audio permissions** when prompted
- Check your **speaker/headphone** volume
- Click the **Test button** above

**Quick fix:** The app will work with fallback responses even if the AI model fails!
""")
