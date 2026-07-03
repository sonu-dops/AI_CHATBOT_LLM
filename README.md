# 🧠 AI_CHATBOT_LLM

An advanced AI-powered chatbot workspace built with **Streamlit** and **Google Gemini 2.5**, featuring persistent multi-session conversations, image & PDF understanding, AI personas, Google Search grounding, streaming responses, and SQLite-based chat history.

---

## 🚀 Features

- 🤖 Google Gemini 2.5 Flash & Pro support
- 💬 Multi-session chat history
- 🗄️ SQLite database for persistent conversations
- 📄 PDF document analysis
- 🖼️ Image understanding
- 🌐 Google Search grounding for up-to-date responses
- ⚡ Real-time streaming AI responses
- 🎭 Multiple AI Personas
  - General Assistant
  - Code Wizard
  - Data Analyst
  - Creative Writer
- 📊 Token usage tracking
- 📥 Export chat history as Markdown
- 🎨 Modern Streamlit interface with Lottie animations

---

# 📸 Preview

> *(Add screenshots of your application here after uploading them to GitHub.)*

Example:

```
assets/
│
├── home.png
├── sidebar.png
└── chat.png
```

Then display them:

```md
![Home](assets/home.png)

![Sidebar](assets/sidebar.png)

![Chat](assets/chat.png)
```

---

# 📁 Project Structure

```
AI_CHATBOT_LLM/
│
├── app.py                      # Advanced chatbot application
├── app_basic.py                # Basic version (optional)
├── requirements.txt
├── README.md
├── .gitignore
├── .env                        # Local only (ignored by Git)
│
├── .streamlit/
│   ├── config.toml
│   ├── secrets.toml            # Local only (ignored by Git)
│   └── secrets.toml.example
│
├── assets/
│
└── chat_workspace.db           # Auto-generated
```

---

# 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- SQLite
- Streamlit Lottie
- Requests
- Base64
- UUID
- Google Search Tool

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/sonu-dops/AI_CHATBOT_LLM.git

cd AI_CHATBOT_LLM
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure the Gemini API Key

For security reasons, API keys are **NOT included** in this repository.

Create the following folder if it does not already exist:

```
.streamlit/
```

Inside that folder create:

```
secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

---

## Get Your Free Gemini API Key

Visit:

https://aistudio.google.com/app/apikey

Generate a free API key and paste it into:

```
.streamlit/secrets.toml
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

Your browser will automatically open the application.

---

# 💡 How to Use

1. Launch the application.
2. Create a new chat session.
3. Select your preferred AI Persona.
4. Choose the Gemini model (Flash or Pro).
5. Ask questions or upload:
   - Images
   - PDF documents
6. Receive AI-generated responses in real time.
7. Export chat history as Markdown if needed.

---

# 🎭 Available Personas

| Persona | Description |
|----------|-------------|
| General Assistant | Everyday conversations and general questions |
| Code Wizard | Programming help, debugging, and code generation |
| Data Analyst | Data analysis, statistics, and mathematical reasoning |
| Creative Writer | Storytelling, blogs, and creative writing |

---

# 📄 Supported File Types

- PNG
- JPG
- JPEG
- PDF

---

# 💾 Database

The application automatically creates:

```
chat_workspace.db
```

This stores:

- Chat sessions
- Conversation history
- Session titles

The database is generated automatically on first launch.

---

# 🔒 Security

The following files are intentionally excluded from GitHub:

```
.env

.streamlit/secrets.toml

chat_workspace.db

venv/
```

Never upload your API keys or secret credentials.

---

# 📦 requirements.txt

Install all required packages using:

```bash
pip install -r requirements.txt
```

---

# 🌟 Future Improvements

- 🎤 Voice Chat
- 🔊 Text-to-Speech
- 🎙️ Speech-to-Text
- 📂 Multiple File Upload
- 📑 RAG with Large Documents
- 👥 User Authentication
- ☁️ Cloud Deployment
- 🐳 Docker Support
- 📱 Responsive Mobile UI

---

# 🤝 Contributing

Contributions are welcome.

Feel free to fork the repository, create a new branch, and submit a Pull Request.

---

# 👨‍💻 Author

**Sonu**

GitHub: https://github.com/sonu-dops

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

It helps others discover the project and motivates future improvements.

---

## 📜 License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute it for educational and personal purposes.
