# filename: sammy_web.py
import streamlit as st
import time
import random

# Page configuration
st.set_page_config(
    page_title="Sammy - Your AI Friend",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "friendly"

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = True

if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# Improved browser TTS function
def speak_text(text):
    """Use browser's text-to-speech"""
    import re
    clean_text = re.sub(r'[^\w\s\.\?\!,]', '', text)
    clean_text = clean_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    
    js_code = f"""
    <script>
    function speak() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance('{clean_text}');
            utterance.rate = 0.8;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }}
    }}
    setTimeout(speak, 100);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# Simple speech recognition interface
def create_speech_interface():
    return """
    <div style="text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px; margin: 10px 0;">
        <h3 style="color: #333; margin-bottom: 20px;">🎤 Click & Speak</h3>
        
        <button onclick="startSpeech()" 
                style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                       border: none; color: white; padding: 15px 30px; 
                       border-radius: 25px; font-size: 16px; cursor: pointer;
                       margin: 10px;">
            🎤 Start Speaking
        </button>
        
        <div id="status" style="color: #666; font-size: 14px; margin: 10px;">
            Click the button and speak into your microphone
        </div>
        
        <div id="result" style="margin: 15px; padding: 15px; border: 2px dashed #4ECDC4; 
                               border-radius: 10px; min-height: 60px; background: white;
                               font-size: 16px; color: #333;">
            Your speech will appear here...
        </div>
    </div>

    <script>
    function startSpeech() {{
        if (!('webkitSpeechRecognition' in window)) {{
            document.getElementById('status').innerHTML = '❌ Speech not supported. Use Chrome/Edge.';
            return;
        }}
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {{
            document.getElementById('status').innerHTML = '🎤 Listening... Speak now!';
            document.getElementById('result').innerHTML = 'Listening...';
        }};
        
        recognition.onresult = function(event) {{
            const transcript = event.results[0][0].transcript;
            document.getElementById('result').innerHTML = '<strong>You said:</strong> ' + transcript;
            document.getElementById('status').innerHTML = '✅ Speech recognized!';
            
            // Store transcript in a hidden input and submit
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.id = 'speechResult';
            hiddenInput.value = transcript;
            document.body.appendChild(hiddenInput);
            
            // Wait a moment then trigger Streamlit
            setTimeout(() => {{
                // This will be handled by the custom component
                window.parent.postMessage({{type: 'speech', text: transcript}}, '*');
            }}, 500);
        }};
        
        recognition.onerror = function(event) {{
            document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
            document.getElementById('result').innerHTML = 'Please try again.';
        }};
        
        recognition.onend = function() {{
            document.getElementById('status').innerHTML = 'Ready to listen again';
        }};
        
        recognition.start();
    }}
    </script>
    """

# JavaScript handler for speech results
def speech_handler_js():
    return """
    <script>
    // Listen for speech results
    window.addEventListener('message', function(event) {
        if (event.data.type === 'speech') {
            // Create a form to submit to Streamlit
            const form = document.createElement('form');
            form.method = 'POST';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'speech_text';
            input.value = event.data.text;
            form.appendChild(input);
            
            document.body.appendChild(form);
            form.submit();
        }
    });
    </script>
    """

# Rule-based Sammy responses
def get_sammy_response(user_message, mode):
    """Generate responses based on rules and patterns"""
    
    user_message_lower = user_message.lower()
    
    # Friendly mode responses
    friendly_responses = {
        'hello': ["Hi there! 😊 How are you doing today?", "Hello! It's great to hear from you!"],
        'hi': ["Hey! 👋 How's your day going?", "Hi there! Nice to chat with you!"],
        'hey': ["Hey! What's up? 😄", "Hey there! How can I help you today?"],
        'how are you': ["I'm doing great, thanks for asking! Ready to chat with you. 😊", "I'm wonderful! How about you?"],
        
        'sad': ["I'm sorry you're feeling sad. 💙 Remember that feelings are temporary.", "I'm here for you. Sometimes talking helps."],
        'happy': ["That's wonderful! 😄 I'm so glad you're feeling happy!", "Yay! Happiness is contagious!"],
        'stressed': ["I understand stress can be overwhelming. 🧘 Try taking a deep breath.", "Stress is tough. What's specifically stressing you out?"],
        
        'default': [
            "That's interesting! Tell me more about that. 😊",
            "I'd love to hear more about your thoughts on that!",
            "How does that make you feel?",
            "What's been on your mind lately?",
            "I'm here to listen whenever you want to share! 💬"
        ]
    }
    
    # Project mode responses
    project_responses = {
        'help': ["I'd be happy to help! What project are you working on? 🛠️", "Tell me about your project!"],
        'project': ["Great! Let's talk about your project. What's the main goal? 🎯", "Projects are exciting!"],
        'idea': ["I love brainstorming! 💡 Tell me about your idea!", "New ideas are wonderful!"],
        
        'default': [
            "Let's break that down into actionable steps! 📝",
            "That's a great starting point! What resources do you need? 🛠️",
            "I like your approach! What's the timeline? ⏰",
            "Good thinking! What challenges do you foresee? 🚧"
        ]
    }
    
    responses = friendly_responses if mode == "friendly" else project_responses
    
    for keyword, response_list in responses.items():
        if keyword != 'default' and keyword in user_message_lower:
            return random.choice(response_list)
    
    return random.choice(responses['default'])

# Main app
st.title("🤖 Sammy - Your AI Companion")
st.markdown("**Chat with your AI friend!** 🎤→🤖→🔊")

# Debug info
if st.sidebar.button("Debug Info"):
    st.sidebar.write(f"Messages: {len(st.session_state.messages)}")
    st.sidebar.write(f"Last input: {st.session_state.last_input}")

# Speech interface
st.markdown("---")
st.subheader("🎤 Speech Input")

# Add the speech handler first
st.components.v1.html(speech_handler_js(), height=0)

# Add speech interface
st.components.v1.html(create_speech_interface(), height=300)

# Handle speech input from form
if st.session_state.get('speech_text'):
    user_input = st.session_state.speech_text
    st.session_state.last_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response
    response = get_sammy_response(user_input, st.session_state.mode)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Speak the response
    speak_text(response)
    
    # Clear the speech input
    st.session_state.speech_text = ""
    st.rerun()

# Manual text input
st.markdown("---")
st.subheader("💬 Text Input")

user_input = st.text_input("Type your message here:", key="text_input")
if st.button("📤 Send Message", type="primary"):
    if user_input.strip():
        st.session_state.last_input = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        response = get_sammy_response(user_input, st.session_state.mode)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Speak the response
        if st.session_state.auto_speak:
            speak_text(response)
        
        st.rerun()

# Mode selection
st.markdown("---")
st.subheader("🎯 Conversation Mode")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Mode", use_container_width=True):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True):
        st.session_state.mode = "project"
        st.session_state.messages = []
        st.rerun()

st.success(f"Mode: {'💬 Friendly' if st.session_state.mode == 'friendly' else '💻 Project'}")

# Display conversation
st.markdown("---")
st.subheader("📝 Conversation")

if not st.session_state.messages:
    st.info("No messages yet. Use speech or text input above to start chatting!")
    st.info("Try saying: 'Hello' or 'Hi Sammy'")
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

# Auto-speak toggle
st.markdown("---")
st.subheader("🔊 Settings")
auto_speak = st.toggle("Auto-speak responses", value=st.session_state.auto_speak)
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak

# Test button
if st.button("🔊 Test Text-to-Speech"):
    test_text = "Hello! This is a test of Sammy's voice. If you can hear this, everything is working!"
    speak_text(test_text)
    st.success("Test message sent! You should hear Sammy speak.")

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.last_input = ""
    st.rerun()

# Sidebar instructions
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    **Speech-to-Speech:**
    1. Click **🎤 Start Speaking**
    2. Allow microphone access
    3. Speak clearly
    4. Sammy will respond verbally
    
    **Text Chat:**
    1. Type in the text box
    2. Click **Send Message**
    3. Sammy will respond
    
    **Requirements:**
    - Chrome/Edge browser
    - Microphone access
    - Audio permissions
    """)
    
    st.header("🎯 Quick Starters")
    st.markdown("""
    Try saying:
    - *Hello Sammy*
    - *How are you?*
    - *I need help*
    - *I'm happy today*
    """)

# Instructions
st.markdown("---")
st.info("""
**Troubleshooting:**
- Use **Chrome/Edge** for best results
- **Allow microphone** when prompted
- **Speak clearly** and not too fast
- **Refresh the page** if issues persist
- **Test TTS** with the button above
""")

# Force a rerun if there are messages but no recent input
if st.session_state.messages and not st.session_state.last_input:
    st.rerun()

