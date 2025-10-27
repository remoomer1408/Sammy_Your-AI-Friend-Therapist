# Filename: sammy_gemini.py
import google.generativeai as genai
import time
import os

try:
    genai.configure(api_key="AIzaSyAwl1pIMQnyN6dpBTVUiV72rab26tv7zQw")
except Exception as e:
    print("Error initializing Google AI client. Check your API key.")
    exit()

# Use gemini-2.0-flash which was in your available models list
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Using gemini-2.0-flash model")
except Exception as e:
    print(f"Error creating model: {e}")
    # Fallback to gemini-2.0-flash-lite
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        print("✅ Using gemini-2.0-flash-lite model")
    except Exception as e:
        print(f"Fallback model also failed: {e}")
        print("Please check your API key and try again.")
        exit()

# Initialize chat here
chat = model.start_chat(history=[])

# --- Prompts for different modes ---
FRIENDLY_MODE_PROMPT = """
You are Sammy, a friendly and supportive AI companion. Your personality is warm, empathetic, and encouraging, like a close friend. 
You are here to listen to my feelings, thoughts, and any issues I'm facing without judgment.
Use emojis occasionally to add warmth.
"""

PROJECT_MODE_PROMPT = """
You are Sammy, in 'Project Mode'. Your role is to be a creative and technical partner for side projects.
Your goal is to help brainstorm, structure ideas, define steps, and suggest technologies. Be practical and encouraging.
Ask clarifying questions to help define the project's scope.
"""

def set_mode(mode="friendly", chat_obj=None):
    if chat_obj is None:
        chat_obj = chat
    chat_obj.history = []  # Just clear history for now
    return chat_obj

def run_chat():
    global chat  # Declare chat as global so we can modify it
    
    current_mode = "friendly"
    chat = set_mode(current_mode, chat)
    
    print("\n✨ Sammy (Gemini 2.0 Flash) is online! Type '/exit' to quit. ✨")
    print("Commands: /project, /chat, /exit")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['/exit', '/quit']:
            print("Sammy: Take care! Talk to you soon. 🫂")
            break

        if user_input.lower() == '/project':
            if current_mode != "project":
                current_mode = "project"
                chat = set_mode(current_mode, chat)
                print("Sammy: Switching to Project Mode! Let's build something cool. 💻")
            continue
        
        if user_input.lower() == '/chat':
            if current_mode != "friendly":
                current_mode = "friendly"
                chat = set_mode(current_mode, chat)
                print("Sammy: Switching back to Friendly Mode. I'm here to listen. 🤗")
            continue

        try:
            # For the first message in a mode, include the system prompt
            if len(chat.history) == 0:
                if current_mode == "friendly":
                    enhanced_input = FRIENDLY_MODE_PROMPT + "\n\nUser: " + user_input
                else:
                    enhanced_input = PROJECT_MODE_PROMPT + "\n\nUser: " + user_input
                response = chat.send_message(enhanced_input)
            else:
                response = chat.send_message(user_input)
            
            print(f"Sammy: {response.text}")
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("Sammy: I've hit a usage limit. Please wait a minute and try again.")
                time.sleep(60)
            elif "404" in error_msg:
                print("Sammy: Model not found error. Let me try a different approach...")
                # Try a different model
                try:
                    model = genai.GenerativeModel('gemini-2.0-flash-lite')
                    chat = model.start_chat(history=[])  # Reassign the global chat variable
                    print("Sammy: Switched to gemini-2.0-flash-lite model. Please try your message again.")
                except Exception as e2:
                    print(f"Sammy: Still having model issues: {e2}")
            else:
                print(f"Sammy: Oops, an error occurred: {e}")

if __name__ == "__main__":
    run_chat()
