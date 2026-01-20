# 🎙️ Vaani AI — Instant Voice Assistant

Vaani AI is a **stateless, real-time voice assistant** built using Streamlit and OpenAI.  
It captures user speech, transcribes it accurately, processes the request using an LLM, and responds with natural AI-generated voice — all in a single interaction.

---

## 🚀 Key Highlights

- 🎤 Push-to-talk microphone input
- 🗣️ High-accuracy speech-to-text using **OpenAI Whisper**
- 🧠 Intelligent responses via **GPT (LangChain)**
- 🔊 Natural AI voice output using **OpenAI Text-to-Speech**
- 🌐 Language hint support (Hindi / English / Auto)
- 🔒 Stateless & privacy-friendly (no history stored)

---

## 🧠 How Vaani AI Works

1. User records voice input
2. Audio is transcribed using Whisper (`whisper-1`)
3. Text is processed by GPT (no chat memory)
4. AI response is converted to speech
5. Audio response is played automatically

Each interaction is **independent and ephemeral**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-----|-----------|
| UI | Streamlit |
| Audio Input | streamlit-mic-recorder |
| Speech-to-Text | OpenAI Whisper |
| LLM | OpenAI GPT via LangChain |
| Text-to-Speech | OpenAI TTS |
| Config | python-dotenv |

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd vaani-ai
2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key

▶️ Run the Application
streamlit run app.py


The application will open automatically in your browser.

🎧 Usage Guide

Select Input Language Hint (Hindi / English)

Click 🎙️ Start Talking

Speak your query

Click 🛑 Stop & Send

Listen to the AI-generated voice response

⚙️ Configuration Notes

Transcription language can be forced (e.g., Hindi) to avoid incorrect scripts

Assistant responses are:

English only

Maximum 2 sentences

Voice styles can be changed from the sidebar

🔐 Privacy & Design Philosophy

❌ No conversation history

❌ No audio storage

✅ Each request is processed independently

Vaani AI is designed for fast, private, and disposable voice interactions.