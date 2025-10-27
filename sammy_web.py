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

# Initialize Gemini
@st.cache_resource
def init_gemini():
    try:
        genai.configure(api_key="AIzaSyAwl1pIMQnyN6dpBTVUiV72rab26tv7zQw")
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

# Sammy's personality prompts
FRIENDLY_MODE_PROMPT = """
You are Sammy, a friendly and supportive AI companion. Your personality is warm, empathetic, and encouraging, like a close friend. 
You are here to listen to my feelings, thoughts, and any issues I'm facing without judgment.
Use emojis occasionally to add warmth. Be conversational and caring.
"""

PROJECT_MODE_PROMPT = """
You are Sammy, in 'Project Mode'. Your role is to be a creative and technical partner for side projects.
Your goal is to help brainstorm, structure ideas, define steps, and suggest technologies. Be practical and encouraging.
Ask clarifying questions to help define the project's scope.
"""

# App title and description
st.title("🤖 Sammy - Your AI Companion")
st.markdown("""
Hi! I'm Sammy, your friendly AI assistant. I'm here to chat about your day or help you with creative projects!
""")

# Mode selection
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Friendly Chat Mode", use_container_width=True):
        st.session_state.mode = "friendly"
        st.session_state.messages = []
        st.rerun()
with col2:
    if st.button("💻 Project Mode", use_container_width=True):
        st.session_state.mode = "project"
        st.session_state.messages = []
        st.rerun()

# Display current mode
mode_emoji = "💬" if st.session_state.mode == "friendly" else "💻"
st.success(f"Current mode: {mode_emoji} {st.session_state.mode.title()} Mode")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
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
                        response = st.session_state.chat.send_message(enhanced_prompt)
                    else:
                        response = st.session_state.chat.send_message(prompt)
                    
                    # Display Sammy's response
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower():
                        st.error("Sammy: I've hit a usage limit. Please wait a minute and try again.")
                    else:
                        st.error(f"Sammy: Oops, an error occurred: {e}")
    else:
        st.error("Sammy is not properly initialized. Please check your API key.")

# Sidebar with info
with st.sidebar:
    st.header("About Sammy")
    st.markdown("""
    **Sammy can help you with:**
    - 🫂 Emotional support and friendly chat
    - 💡 Brainstorming creative ideas
    - 🚀 Planning side projects
    - 📝 Breaking down complex tasks
    
    **Commands:**
    - Switch between modes using the buttons above
    - Just start typing to chat!
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if st.session_state.chat:
            st.session_state.chat.history = []
        st.rerun()
