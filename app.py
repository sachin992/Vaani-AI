
import streamlit as st
import os
import tempfile
from streamlit_mic_recorder import mic_recorder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Page Config & Styling ---
st.set_page_config(page_title="Instant Voice AI", page_icon="🎤", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    :root {
        --surface: rgba(255, 255, 255, 0.84);
        --surface-border: rgba(12, 28, 50, 0.12);
        --ink: #0f1a2e;
        --muted: #53627a;
        --accent: #0b7fab;
        --accent-2: #23a8c6;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(235, 255, 224, 0.8) 0%, transparent 34%),
            radial-gradient(circle at 86% 10%, rgba(199, 235, 255, 0.75) 0%, transparent 38%),
            radial-gradient(circle at 60% 84%, rgba(255, 229, 197, 0.7) 0%, transparent 32%),
            linear-gradient(145deg, #f6fbff 0%, #fdf8f1 45%, #f3f8ff 100%);
        color: var(--ink);
        font-family: 'Manrope', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    .hero-wrap {
        border: 1px solid var(--surface-border);
        background: var(--surface);
        border-radius: 20px;
        padding: 1.2rem 1.2rem 0.9rem 1.2rem;
        box-shadow: 0 18px 36px rgba(20, 36, 56, 0.08);
        margin-bottom: 0.8rem;
    }

    .hero-kicker {
        color: var(--accent);
        font-weight: 800;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .hero-sub {
        color: var(--muted);
        margin: 0.2rem 0 0.1rem 0;
        font-size: 0.95rem;
    }

    .status-row {
        display: flex;
        gap: 0.45rem;
        flex-wrap: wrap;
        margin-top: 0.85rem;
    }

    .status-pill {
        border-radius: 999px;
        padding: 0.33rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid rgba(11, 127, 171, 0.22);
        color: #14546c;
        background: rgba(35, 168, 198, 0.1);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(245,251,255,0.94) 100%);
        border-right: 1px solid rgba(15, 26, 46, 0.08);
    }

    .stSelectbox label, .stCaption {
        color: #304159 !important;
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid rgba(11, 127, 171, 0.25);
        background: linear-gradient(140deg, #0b7fab 0%, #23a8c6 100%);
        color: white;
        min-height: 2.95rem;
        font-weight: 700;
        box-shadow: 0 10px 18px rgba(16, 84, 117, 0.22);
        transition: transform 160ms ease, box-shadow 160ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 22px rgba(16, 84, 117, 0.28);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        border: 1px solid rgba(12, 28, 50, 0.08);
        background: rgba(255, 255, 255, 0.76);
        backdrop-filter: blur(2px);
    }

    @media (max-width: 768px) {
        .hero-wrap {
            border-radius: 16px;
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-kicker">Vaani AI</div>
      <h1 style="margin: 0;">🎙️ Instant Voice Assistant</h1>
      <p class="hero-sub">Speak naturally, get a concise answer instantly, and hear it back in your selected AI voice.</p>
      <div class="status-row">
        <span class="status-pill">Real-time Flow</span>
        <span class="status-pill">No History</span>
        <span class="status-pill">One-shot Privacy</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Clients ---
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- Sidebar ---
with st.sidebar:
    st.header("Voice Studio")
    voice_type = st.selectbox("Assistant Voice", ["nova", "alloy", "shimmer", "echo", "onyx", "fable"])
    
    # NEW: Language selection to prevent Urdu transcription
    input_lang = st.selectbox(
        "Input Language Hint", 
        ["Auto-detect", "Hindi", "English"],
        index=0  # Default to Auto-detect
    )
    
    lang_code = None
    if input_lang == "Hindi":
        lang_code = "hi"
    elif input_lang == "English":
        lang_code = "en"

    st.caption("No history is stored. Each interaction is fresh and independent.")

# --- Recording Interface ---
audio_record = mic_recorder(
    start_prompt="🎙️ Start Talking",
    stop_prompt="🛑 Stop & Send",
    key='voice_input',
    use_container_width=True
)

# --- Standalone Processing Pipeline ---
if audio_record:
    try:
        recorded_bytes = audio_record.get('bytes', b'')
        if not recorded_bytes or len(recorded_bytes) < 3000:
            st.warning("I could not hear a clear voice sample. Please speak a little longer and try again.")
            st.stop()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(recorded_bytes)
            temp_path = f.name

        with st.status("Processing Voice...", expanded=True) as status:
            
            # 1. Transcribe (Whisper)
            status.write("Transcribing audio...")
            with open(temp_path, "rb") as audio_file:
                transcription_args = {
                    "model": "whisper-1",
                    "file": audio_file,
                }
                if lang_code:
                    transcription_args["language"] = lang_code
                transcription = client.audio.transcriptions.create(**transcription_args)
            user_text = (transcription.text or "").strip()
            if not user_text:
                status.update(label="Could not detect speech", state="error")
                st.warning("Speech was unclear. Try speaking closer to the mic and reduce background noise.")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                st.stop()
            
            # 2. Brain (LLM - No History)
            status.write(f"Thinking about: '{user_text}'")
            response = llm.invoke([
                SystemMessage(content="You are a professional voice assistant. Respond ONLY in English. Keep your answers very brief, maximum 2 sentences."),
                HumanMessage(content=user_text)
            ])
            ai_content = response.content

            # 3. Speak (TTS)
            status.write("Generating voice response...")
            speech = client.audio.speech.create(
                model="tts-1", 
                voice=voice_type,
                input=ai_content
            )
            audio_bytes = speech.read()
            
            status.update(label="Response Ready!", state="complete")

        # --- Visual Output ---
        st.chat_message("user").write(user_text)
        st.chat_message("assistant").write(ai_content)
        
        # --- Audio Output & Autoplay ---
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.caption("🤖 This assistant treats every recording as a new conversation.")