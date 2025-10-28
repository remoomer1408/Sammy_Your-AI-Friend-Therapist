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

# Speech-to-Text functionality
def create_speech_to_text_interface():
    """Create a complete speech-to-text interface"""
    return """
    <div style="text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px; margin: 10px 0;">
        <h3 style="color: #333; margin-bottom: 20px;">🎤 Speech-to-Text</h3>
        
        <button onclick="startListening()" id="listenBtn" 
                style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                       border: none; color: white; padding: 15px 30px; 
                       border-radius: 25px; font-size: 16px; cursor: pointer;
                       margin: 10px; transition: all 0.3s;">
            🎤 Start Listening
        </button>
        
        <button onclick="stopListening()" id="stopBtn" 
                style="background: #666; border: none; color: white; 
                       padding: 15px 30px; border-radius: 25px; 
                       font-size: 16px; cursor: pointer; margin: 10px;
                       display: none;">
            ⏹️ Stop Listening
        </button>
        
        <div id="status" style="color: #666; font-size: 14px; margin: 10px;">
            Click "Start Listening" and speak into your microphone
        </div>
        
        <div id="result" style="margin: 15px; padding: 15px; border: 2px dashed #4ECDC4; 
                               border-radius: 10px; min-height: 60px; background: white;
                               font-size: 16px; color: #333;">
            Your speech will appear here...
        </div>
        
        <button onclick="sendToSammy()" id="sendBtn" 
                style="background: #2196F3; border: none; color: white; 
                       padding: 12px 25px; border-radius: 20px; 
                       font-size: 14px; cursor: pointer; margin: 5px;
                       display: none;">
            📤 Send to Sammy
        </button>
    </div>

    <script>
    let recognition;
    let isListening = false;
    let currentTranscript = "";
    
    function initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                isListening = true;
                updateButtonState();
                document.getElementById('status').innerHTML = '🎤 <strong>Listening...</strong> Speak now!';
                document.getElementById('status').style.color = '#4CAF50';
            };
            
            recognition.onresult = function(event) {
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                currentTranscript = finalTranscript || interimTranscript;
                document.getElementById('result').innerHTML = '<strong>You said:</strong> ' + currentTranscript;
                
                // Auto-send if there's a final transcript and auto-mode is enabled
                if (finalTranscript && window.autoSendMode) {
                    sendToSammy();
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
                document.getElementById('status').style.color = '#FF6B6B';
                stopListening();
            };
            
            recognition.onend = function() {
                isListening = false;
                updateButtonState();
                document.getElementById('status').innerHTML = 'Ready to listen again';
                document.getElementById('status').style.color = '#666';
            };
            
            return true;
        } else {
            document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome or Edge.';
            return false;
        }
    }
    
    function startListening() {
        if (!recognition) {
            if (!initializeSpeechRecognition()) return;
        }
        
        if (!isListening) {
            recognition.start();
        }
    }
    
    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
        }
    }
    
    function updateButtonState() {
        const listenBtn = document.getElementById('listenBtn');
        const stopBtn = document.getElementById('stopBtn');
        const sendBtn = document.getElementById('sendBtn');
        
        if (isListening) {
            listenBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
            sendBtn.style.display = 'inline-block';
        } else {
            listenBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            sendBtn.style.display = currentTranscript ? 'inline-block' : 'none';
        }
    }
    
    function sendToSammy() {
        if (currentTranscript) {
            // Create a form to submit to Streamlit
            const form = document.createElement('form');
            form.method = 'POST';
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'speech_input';
            input.value = currentTranscript;
            form.appendChild(input);
            document.body.appendChild(form);
            
            // Reset for next interaction
            currentTranscript = "";
            document.getElementById('result').innerHTML = 'Your speech will appear here...';
            document.getElementById('sendBtn').style.display = 'none';
            
            // Submit the form
            form.submit();
        }
    }
    
    // Initialize when page loads
    window.addEventListener('load', function() {
        initializeSpeechRecognition();
    });
    </script>
    """

# Rule-based Sammy responses
def get_sammy_response(user_message, mode, conversation_history):
    """Generate responses based on rules and patterns"""
    
    user_message_lower = user_message.lower()
    
    # Friendly mode responses
    friendly_responses = {
        'hello': ["Hi there! 😊 How are you doing today?", "Hello! It's great to hear from you!"],
        'hi': ["Hey! 👋 How's your day going?", "Hi there! Nice to chat with you!"],
        'hey': ["Hey! What's up? 😄", "Hey there! How can I help you today?"],
        'how are you': ["I'm doing great, thanks for asking! Ready to chat with you. 😊", "I'm wonderful! How about you?"],
        'good morning': ["Good morning! 🌞 Hope you have a wonderful day ahead!", "Morning! What's on your agenda today?"],
        'good night': ["Good night! 🌙 Sleep well and sweet dreams!", "Night night! Hope you rest well!"],
        
        'sad': ["I'm sorry you're feeling sad. 💙 Remember that feelings are temporary. Want to talk about it?", "I'm here for you. Sometimes talking helps. Would you like to share?"],
        'happy': ["That's wonderful! 😄 I'm so glad you're feeling happy! What's making you smile?", "Yay! Happiness is contagious! Tell me more!"],
        'stressed': ["I understand stress can be overwhelming. 🧘 Try taking a deep breath. One step at a time.", "Stress is tough. What's specifically stressing you out?"],
        'anxious': ["Anxiety can be challenging. 🌸 Remember to breathe deeply. This feeling will pass.", "I'm here with you. Try naming 3 things you can see around you."],
        'tired': ["It's okay to feel tired. 🛌 Remember to rest when you need to. You deserve breaks!", "Tiredness happens. Maybe a short break would help?"],
        
        'thank you': ["You're welcome! 😊 I'm always here to chat with you.", "Anytime! I enjoy our conversations!"],
        'bye': ["Goodbye! 👋 Hope to chat with you again soon!", "Bye! Take care and talk to you later!"],
        
        'default': [
            "That's interesting! Tell me more about that. 😊",
            "I'd love to hear more about your thoughts on that!",
            "How does that make you feel?",
            "What's been on your mind lately?",
            "I'm here to listen whenever you want to share! 💬",
            "That sounds important to you. Would you like to explore that further?",
            "Thanks for sharing that with me!",
            "I appreciate you opening up! How can I support you?",
            "That's really thoughtful! What inspired that?",
            "I'm listening! Feel free to share as much as you'd like. 🌟"
        ]
    }
    
    # Project mode responses
    project_responses = {
        'help': ["I'd be happy to help! What project are you working on? 🛠️", "Tell me about your project!"],
        'project': ["Great! Let's talk about your project. What's the main goal? 🎯", "Projects are exciting! What stage are you at?"],
        'idea': ["I love brainstorming! 💡 Tell me about your idea!", "New ideas are wonderful! What's sparked this one?"],
        'stuck': ["When you're stuck, sometimes taking a break helps! 🚶 What specific part is tricky?", "Let's break this down. What's the next small step?"],
        'plan': ["Planning is key! 📋 What's your timeline? Let's create milestones.", "Good planning makes execution easier."],
        'task': ["What's the specific task you're working on? 📝", "Let's break that task into smaller steps!"],
        'goal': ["What's your main goal? 🎯 That'll help us focus.", "Great! What does success look like for this goal?"],
        
        'default': [
            "Let's break that down into actionable steps! What's first? 📝",
            "That's a great starting point! What resources do you need? 🛠️",
            "I like your approach! What's the timeline? ⏰",
            "Good thinking! What challenges do you foresee? 🚧",
            "Let's create some milestones! What would success look like? 🎯",
            "What's the most important priority right now? 🔥",
            "Have you considered breaking this into smaller tasks? 📋",
            "What support do you need to make this happen? 🤝",
            "Let's think about the next immediate action! ➡️",
            "That's progress! What's the biggest obstacle? 🏔️"
        ]
    }
    
    responses = friendly_responses if mode == "friendly" else project_responses
    
    for keyword, response_list in responses.items():
        if keyword != 'default' and keyword in user_message_lower:
            return random.choice(response_list)
    
    return random.choice(responses['default'])

# Initialize app state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "friendly"

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = True  # Default to True for speech-to-speech

if "auto_send" not in st.session_state:
    st.session_state.auto_send = True  # Auto-send after speech

# Main app
st.title("🤖 Sammy - Your AI Companion")
st.markdown("**Now with Complete Speech-to-Speech Conversation!** 🎤→🤖→🔊")

# Speech-to-Speech Controls
st.markdown("---")
st.subheader("🎤 Speech-to-Speech Conversation")

# Auto-send toggle (send automatically after speech)
auto_send = st.toggle("Auto-send after speech", value=st.session_state.auto_send, key="auto_send_toggle")
if auto_send != st.session_state.auto_send:
    st.session_state.auto_send = auto_send

# Display the speech-to-text interface
st.components.v1.html(create_speech_to_text_interface(), height=400)

# Add JavaScript for auto-send mode
if st.session_state.auto_send:
    st.markdown("""
    <script>
    window.autoSendMode = true;
    </script>
    """, unsafe_allow_html=True)

# Mode selection
st.markdown("---")
st.subheader("🎯 Conversation Mode")
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 **Friendly Chat Mode**", use_container_width=True, key="btn_friendly"):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        st.rerun()
with col2:
    if st.button("💻 **Project Helper Mode**", use_container_width=True, key="btn_project"):
        st.session_state.mode = "project"
        st.session_state.messages = []
        st.rerun()

st.success(f"**Current Mode:** {'💬 Friendly Chat' if st.session_state.mode == 'friendly' else '💻 Project Helper'}")

# Manual text input fallback
st.markdown("---")
st.subheader("💬 Manual Input (Fallback)")
user_input = st.text_area("Or type your message here:", height=80, key="user_input")
if st.button("📤 Send Text Message", key="btn_send_text"):
    if user_input.strip():
        st.session_state.process_input = user_input.strip()

# Process speech input
if st.session_state.get('speech_input'):
    prompt = st.session_state.speech_input
    del st.session_state.speech_input
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get and speak Sammy's response
    with st.spinner("Sammy is thinking and speaking..."):
        response = get_sammy_response(prompt, st.session_state.mode, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Always speak in speech-to-speech mode
        time.sleep(0.5)
        speak_text(response)
    
    st.rerun()

# Process manual input
if st.session_state.get('process_input'):
    prompt = st.session_state.process_input
    del st.session_state.process_input
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Sammy is thinking..."):
        response = get_sammy_response(prompt, st.session_state.mode, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        if st.session_state.auto_speak:
            time.sleep(0.5)
            speak_text(response)
    
    st.rerun()

# Display conversation
st.markdown("---")
st.subheader("📝 Conversation History")

if not st.session_state.messages:
    st.info("No messages yet. Use the speech interface above to start talking!")
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
    st.header("⚙️ Speech Settings")
    
    # Auto-speak toggle
    auto_speak = st.toggle("Auto-speak responses", value=st.session_state.auto_speak, key="sidebar_auto_speak")
    if auto_speak != st.session_state.auto_speak:
        st.session_state.auto_speak = auto_speak
    
    if st.button("🗑️ Clear Conversation", use_container_width=True, key="btn_clear"):
        st.session_state.messages = []
        st.rerun()
    
    st.header("📊 Session Info")
    st.write(f"**Messages:** {len(st.session_state.messages)}")
    st.write(f"**Mode:** {'Friendly' if st.session_state.mode == 'friendly' else 'Project'}")
    st.write(f"**Auto-speak:** {'✅ On' if st.session_state.auto_speak else '❌ Off'}")
    st.write(f"**Auto-send:** {'✅ On' if st.session_state.auto_send else '❌ Off'}")
    
    st.header("🎤 Speech Guide")
    st.markdown("""
    **For Speech-to-Speech:**
    1. Click **🎤 Start Listening**
    2. **Allow microphone access**
    3. **Speak naturally**
    4. Sammy will **respond verbally**
    
    **Best with:**
    - Google Chrome
    - Microphone enabled
    - Good internet connection
    
    **Try saying:**
    - "Hello Sammy"
    - "How are you?"
    - "I need help with a project"
    - "I'm feeling happy today"
    """)

# Instructions
st.markdown("---")
st.success("""
**🎉 Complete Speech-to-Speech Conversation Ready!**

**How to have a voice conversation:**
1. **Click "🎤 Start Listening"** above
2. **Allow microphone access** when prompted  
3. **Speak naturally** - you'll see your words appear
4. **Sammy will respond verbally** automatically
5. **Continue speaking** for a full conversation

**💡 Pro Tip:** Enable "Auto-send after speech" for seamless voice chatting!
""")

# Additional JavaScript for better speech handling
st.markdown("""
<script>
// Enhanced speech recognition handling
function checkCompatibility() {
    if ('webkitSpeechRecognition' in window) {
        console.log('Speech recognition: Supported');
        return true;
    } else {
        console.log('Speech recognition: Not supported');
        return false;
    }
}

// Initialize compatibility check
window.addEventListener('load', checkCompatibility);
</script>
""", unsafe_allow_html=True)
