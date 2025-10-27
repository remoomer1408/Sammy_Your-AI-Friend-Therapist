# 🤖 Sammy - Your Personal AI Companion

![Sammy AI](https://img.shields.io/badge/Sammy-AI%20Friend-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Google-Gemini%20AI-yellow?style=for-the-badge)

**Sammy** is your personal AI friend and project partner, built with Streamlit and powered by Google's Gemini AI. Whether you need emotional support, creative brainstorming, or project planning, Sammy is here to help!

✨ Features

- **💬 Friendly Chat Mode**: Get emotional support and have meaningful conversations
- **💻 Project Mode**: Brainstorm ideas and plan side projects with structured guidance
- **🎯 Smart Context Switching**: Seamlessly switch between different modes
- **🌐 Web Interface**: Beautiful, responsive web app built with Streamlit
- **💾 Conversation Memory**: Remembers your chat history within each session

🚀 Quick Start

Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/sammy-ai-app.git
   cd sammy-ai-app
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   - Create a `.streamlit/secrets.toml` file:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```

4. **Run the app locally**
   ```bash
   streamlit run sammy_web.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🎮 How to Use

Chat Modes
- **Friendly Mode**: Perfect for daily conversations, emotional support, and casual chats
- **Project Mode**: Ideal for brainstorming, planning, and breaking down complex tasks

Commands
- Use the mode buttons to switch between chat styles
- Type naturally - Sammy understands context and maintains conversation flow
- No special commands needed - just chat like you would with a friend!


## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **AI Backend**: Google Gemini AI
- **Programming Language**: Python
- **Deployment**: Streamlit Community Cloud

📁 Project Structure

```
sammy-ai-app/
├── sammy_web.py          # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── .streamlit/
    └── secrets.toml      # API keys (local only, not in repo)
```
🔧 Development

Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run sammy_web.py
```

### Customizing Sammy
You can easily customize Sammy's personality by modifying the prompt templates in `sammy_web.py`:

```python
FRIENDLY_MODE_PROMPT = """
Your custom personality description here...
"""

PROJECT_MODE_PROMPT = """
Your custom project helper description here...
"""
```

🚀 Deployment

Deploy to Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file path to `sammy_web.py`
5. Add your `GEMINI_API_KEY` in the secrets section
6. Deploy!

Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for the powerful language model
- Streamlit for the amazing web framework
- The open-source community for inspiration and tools

## 🆘 Support

If you encounter any issues:

1. Check the [ troubleshooting guide](TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](https://github.com/yourusername/sammy-ai-app/issues)
3. Create a new issue with details about your problem

## 📞 Contact

**Your Name** 
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

<div align="center">

**Made with ❤️ and 🤖 AI**

*If you like this project, don't forget to give it a ⭐!*



🎯 Roadmap

- [ ] Voice interaction support
- [ ] File upload for project discussions
- [ ] Conversation history saving
- [ ] Multiple language support
- [ ] Mobile app version

---

**Happy chatting with Sammy!** 🎉
