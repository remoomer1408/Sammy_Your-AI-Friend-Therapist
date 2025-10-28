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
    # Clean the text for JavaScript
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
            window.speechSynthesis.speak(utterance);
        }}
    }}
    setTimeout(speak, 100);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# Rule-based Sammy responses (no API needed)
def get_sammy_response(user_message, mode, conversation_history):
    """Generate responses based on rules and patterns"""
    
    user_message_lower = user_message.lower()
    
    # Friendly mode responses
    friendly_responses = {
        # Greetings
        'hello': ["Hi there! 😊 How are you doing today?", "Hello! It's great to hear from you! What's on your mind?"],
        'hi': ["Hey! 👋 How's your day going?", "Hi there! Nice to chat with you!"],
        'hey': ["Hey! What's up? 😄", "Hey there! How can I help you today?"],
        
        # How are you
        'how are you': ["I'm doing great, thanks for asking! Just here ready to chat with you. 😊", "I'm wonderful! How about you? How's your day going?"],
        
        # Feelings/emotions
        'sad': ["I'm sorry you're feeling sad. 💙 Remember that feelings are temporary and it's okay to not be okay. Want to talk about what's bothering you?", "I'm here for you. Sometimes just talking about what's making us sad can help. Would you like to share?"],
        'happy': ["That's wonderful! 😄 I'm so glad you're feeling happy! What's making you smile today?", "Yay! Happiness is contagious! Tell me more about what's bringing you joy!"],
        'stressed': ["I understand stress can be overwhelming. 🧘 Try taking a deep breath with me. Remember to take things one step at a time.", "Stress is tough. Sometimes breaking things down into smaller tasks can help. What's specifically stressing you out?"],
        'anxious': ["Anxiety can be challenging. 🌸 Remember to breathe deeply. You're stronger than you think, and this feeling will pass.", "I'm here with you. Try naming 3 things you can see around you - it can help ground you in the moment."],
        
        # Questions about Sammy
        'who are you': ["I'm Sammy! 🤖 Your friendly AI companion here to chat, listen, and support you. Think of me as your digital friend!", "I'm Sammy - created to be a good listener and supportive friend. I'm here whenever you need someone to talk to!"],
        'what can you do': ["I can chat with you about your day, help you process feelings, or just keep you company! I'm a good listener. 😊", "I'm here to listen, offer support, and chat about anything on your mind. No judgment, just friendly conversation!"],
        
        # Default responses
        'default': [
            "That's interesting! Tell me more about that. 😊",
            "I'd love to hear more about your thoughts on that!",
            "How does that make you feel?",
            "What's been on your mind lately?",
            "I'm here to listen whenever you want to share! 💬",
            "That sounds important to you. Would you like to explore that further?",
            "Thanks for sharing that with me! What else is happening in your world?",
            "I appreciate you opening up! How can I support you right now?",
            "That's really thoughtful! What inspired that?",
            "I'm listening! Feel free to share as much or as little as you'd like. 🌟"
        ]
    }
    
    # Project mode responses
    project_responses = {
        'help': ["I'd be happy to help! What project are you working on? 🛠️", "Tell me about your project and I'll help you break it down!"],
        'project': ["Great! Let's talk about your project. What's the main goal? 🎯", "Projects are exciting! What stage are you at currently?"],
        'idea': ["I love brainstorming! 💡 Tell me about your idea and we can explore it together.", "New ideas are wonderful! What's sparked this one?"],
        'stuck': ["When you're stuck, sometimes taking a break helps! 🚶 What specific part are you having trouble with?", "Let's break this down. What's the next small step you could take?"],
        'plan': ["Planning is key! 📋 What's your timeline looking like? Let's create some milestones.", "Good planning makes execution easier. What are your main objectives?"],
        
        'default': [
            "Let's break that down into actionable steps! What's the first thing you need to do? 📝",
            "That's a great starting point! What resources do you need to move forward? 🛠️",
            "I like your approach! What's the timeline for this project? ⏰",
            "Good thinking! What potential challenges do you foresee? 🚧",
            "Let's create some milestones! What would success look like for this? 🎯",
            "What's the most important priority right now? 🔥",
            "Have you considered breaking this into smaller tasks? 📋",
            "What support do you need to make this happen? 🤝",
            "Let's think about the next immediate action you can take! ➡️",
            "That's progress! What's the biggest obstacle you're facing? 🏔️"
        ]
    }
    
    # Choose response based on mode
    responses = friendly_responses if mode == "friendly" else project_responses
    
    # Check for specific keywords
    for keyword, response_list in responses.items():
        if keyword != 'default' and keyword in user_message_lower:
            return random.choice(response_list)
    
    # Use default response
    return random.choice(responses['default'])

# Initialize app state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "friendly"

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = False

# Main app
st.title("🤖 Sammy - Your AI Companion")
st.markdown("Chat with your AI friend! **No API key needed!**")

# Mode selection
st.markdown("### 🎯 Choose Conversation Mode")
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
    
    # Get Sammy's response
    with st.spinner("Sammy is thinking..."):
        response = get_sammy_response(prompt, st.session_state.mode, st.session_state.messages)
        
        # Add Sammy's response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Auto-speak if enabled
        if st.session_state.auto_speak:
            time.sleep(0.5)
            speak_text(response)
    
    st.rerun()

# Text-to-Speech Controls
st.markdown("---")
st.subheader("🔊 Text-to-Speech Settings")

# Auto-speak toggle
auto_speak = st.toggle("Automatically speak Sammy's responses", 
                      value=st.session_state.auto_speak,
                      key="toggle_auto_speak")
if auto_speak != st.session_state.auto_speak:
    st.session_state.auto_speak = auto_speak

# Test TTS button
if st.button("🔊 Test Text-to-Speech", key="btn_test_tts"):
    test_text = "Hello! This is Sammy's text-to-speech test. If you can hear this, it's working perfectly!"
    speak_text(test_text)
    st.success("Testing text-to-speech... You should hear a message!")

# Display conversation
st.markdown("---")
st.subheader("📝 Conversation History")

if not st.session_state.messages:
    st.info("No messages yet. Start a conversation above! Try saying 'hello' or 'I need help with a project'")
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
    
    if st.button("🗑️ Clear Chat History", use_container_width=True, key="btn_clear"):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()
    
    st.header("📊 Session Info")
    st.write(f"**Messages:** {len(st.session_state.messages)}")
    st.write(f"**Mode:** {'Friendly Chat' if st.session_state.mode == 'friendly' else 'Project Helper'}")
    st.write(f"**Auto-speak:** {'✅ Enabled' if st.session_state.auto_speak else '❌ Disabled'}")
    
    st.header("💡 Conversation Tips")
    st.markdown("""
    **Try saying:**
    - *Hello* or *Hi*
    - *How are you?*
    - *I'm feeling [sad/happy/stressed]*
    - *I need help with a project*
    - *I have an idea*
    - *I'm stuck on something*
    
    **Friendly Mode:** Emotional support, casual chat
    **Project Mode:** Planning, brainstorming, problem-solving
    """)

# Instructions
st.markdown("---")
st.success("""
**🎉 No API Key Required!** This version of Sammy works completely offline using rule-based responses.

**🔊 Text-to-Speech Tips:**
- Use **Chrome** or **Edge** for best results
- Allow **audio permissions** when prompted
- Click **🔊 buttons** to hear messages
- Enable **auto-speak** for automatic responses

**💬 Conversation Starters:**
- "Hello Sammy!"
- "I'm feeling happy today"
- "I need help planning a project"
- "What can you do?"
""")

# JavaScript for better TTS handling
st.markdown("""
<script>
// Additional TTS support
function checkTTSSupport() {
    if ('speechSynthesis' in window) {
        console.log('Text-to-speech supported');
        return true;
    } else {
        console.log('Text-to-speech not supported');
        return false;
    }
}
checkTTSSupport();
</script>
""", unsafe_allow_html=True)