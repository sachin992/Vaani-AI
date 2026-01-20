
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
    .stButton>button {
        border-radius: 20px;
        height: 3em;
        width: 100%;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Instant Voice Assistant")
st.write("Click 'Start Talking', speak your request, and click 'Stop & Send'.")

# --- Clients ---
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- Sidebar ---
with st.sidebar:
    st.header("Voice Settings")
    voice_type = st.selectbox("Assistant Voice", ["nova", "alloy", "shimmer", "echo", "onyx", "fable"])
    
    # NEW: Language selection to prevent Urdu transcription
    input_lang = st.selectbox(
        "Input Language Hint", 
        ["Auto-detect", "Hindi", "English"],
        index=1  # Default to Hindi
    )
    
    lang_code = None
    if input_lang == "Hindi":
        lang_code = "hi"
    elif input_lang == "English":
        lang_code = "en"

    st.caption("No history is stored. Each interaction is fresh.")

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_record['bytes'])
            temp_path = f.name

        with st.status("Processing Voice...", expanded=True) as status:
            
            # 1. Transcribe (Whisper)
            status.write("Transcribing audio...")
            with open(temp_path, "rb") as audio_file:
                # We add the 'language' parameter here to force Hindi script
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="hi"  # This is the key fix
                )
            user_text = transcription.text
            
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