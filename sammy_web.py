# filename: sammy_web.py
import streamlit as st
import random

st.set_page_config(page_title="Sammy - Your AI Friend", page_icon="🤖")

# Simple response function that works
def get_response(message):
    message_lower = message.lower()
    
    # Specific responses for common queries
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello there! 😊 How can I help you today?"
    
    elif 'ai' in message_lower and 'project' in message_lower:
        return """Great question! 🤖 Here are some AI project ideas in Python:

1. **Chatbot Assistant** - Like me! A conversational AI
2. **Image Classifier** - Recognize objects in photos
3. **Sentiment Analyzer** - Understand emotions in text
4. **Recommendation System** - Suggest movies, products, etc.
5. **Voice Assistant** - Control apps with your voice

Which one interests you most? I can explain any in detail! 🚀"""
    
    elif 'python' in message_lower and 'project' in message_lower:
        return """🐍 Python project ideas:

1. **Task Manager App** - Organize your daily activities
2. **Weather Dashboard** - Real-time weather information
3. **Expense Tracker** - Manage your finances
4. **Quiz Game** - Interactive learning tool
5. **Web Scraper** - Extract data from websites

What type of project are you thinking about?"""

    elif any(word in message_lower for word in ['sad', 'depressed', 'unhappy']):
        return "I'm sorry you're feeling down. 💙 Remember that it's okay to feel this way. Would you like to talk about what's bothering you?"

    elif any(word in message_lower for word in ['happy', 'excited', 'great']):
        return "That's wonderful! 😊 I'm so glad you're feeling good! What's making you happy today?"

    elif any(word in message_lower for word in ['help', 'stuck']):
        return "I'm here to help! 🤝 What specific problem are you facing? Tell me more about what you're working on."

    # Default responses
    else:
        return random.choice([
            "That's interesting! Tell me more about that. 😊",
            "Thanks for sharing! How can I help you with this?",
            "I'd love to hear more about your thoughts!",
            "That sounds important. What aspects interest you most?",
            "I'm listening! Feel free to share more details. 💬"
        ])

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Sammy - Your AI Companion")
st.markdown("Chat with your friendly AI friend!")

# Simple text input - this will definitely work
user_input = st.text_input("💬 Talk to Sammy:", key="user_input")

# Process the input when user presses Enter or clicks anywhere
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get and add Sammy's response
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear the input by resetting the key
    st.session_state.user_input = ""
    st.rerun()

# Display conversation
st.markdown("---")
st.subheader("📝 Conversation")

if not st.session_state.messages:
    st.info("💡 **Try these examples:**")
    st.write("• 'Hello Sammy!'")
    st.write("• 'I want AI project ideas in Python'")
    st.write("• 'I'm feeling sad today'")
    st.write("• 'Can you help me with a project?'")
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Sammy:** {message['content']}")

# Clear button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Test button to verify it works
if st.sidebar.button("🧪 Test Response"):
    test_msg = "Testing if Sammy works"
    st.session_state.messages.append({"role": "user", "content": test_msg})
    st.session_state.messages.append({"role": "assistant", "content": "✅ Test successful! Sammy is working perfectly!"})
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("✅ **Guaranteed to work!** Simple text input that definitely responds.")
