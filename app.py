import json
import streamlit.components.v1 as components
import streamlit as st
import logging
import tempfile
import os
import hashlib

from voice_assistant.config import Config
from voice_assistant.api_key_manager import (
    get_transcription_api_key,
    get_response_api_key,
    get_tts_api_key,
)
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech


logging.basicConfig(level=logging.INFO)

# Cloud configuration: use these three providers initially.
Config.TRANSCRIPTION_MODEL = "groq"
Config.RESPONSE_MODEL = "groq"
Config.TTS_MODEL = "elevenlabs"


def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm SPARK. How can I help you today?"
            }
        ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": (
                    "You are SPARK, a helpful AI voice assistant. "
                    "Answer clearly, naturally, and conversationally. "
                    "Do not claim access to external services or personal "
                    "information unless that information is provided."
                )
            }
        ]

    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None


def process_user_input(user_input):
    if not user_input or not user_input.strip():
        return

    user_input = user_input.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
        response = "Goodbye! It was nice chatting with you."
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        return

    # Generate the AI response.
    try:
        api_key = get_response_api_key()

        if not api_key:
            raise ValueError("Groq API key is missing. Check your configuration.")

        with st.spinner("SPARK is thinking..."):
            response = generate_response(
                Config.RESPONSE_MODEL,
                api_key,
                st.session_state.chat_history,
                Config.LOCAL_MODEL_PATH
            )
            st.session_state.latest_tts_text = response

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

    except Exception as e:
        logging.exception("Response generation failed")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"I couldn't generate a response: {str(e)}"
        })
        return

    # Generate voice output using ElevenLabs.
    output_file = None

   # Store response for browser-side Puter.js TTS.



def process_recording(audio_file):
    if audio_file is None:
        return

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        st.warning("No audio detected. Please try recording again.")
        return

    # Prevent the same recording from being processed repeatedly.
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()

    if audio_hash == st.session_state.last_audio_hash:
        return

    st.session_state.last_audio_hash = audio_hash

    temp_path = None

    try:
        api_key = get_transcription_api_key()

        if not api_key:
            raise ValueError("Groq API key is missing.")

        # Streamlit browser recordings are WAV audio.
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        with st.spinner("SPARK is listening and transcribing..."):
            transcription = transcribe_audio(
                Config.TRANSCRIPTION_MODEL,
                api_key,
                temp_path,
                Config.LOCAL_MODEL_PATH
            )

        if not transcription or not transcription.strip():
            st.warning("No speech detected. Please try again.")
            return

        st.success(f"You said: {transcription}")
        process_user_input(transcription)

    except Exception as e:
        logging.exception("Audio processing failed")
        st.error(f"Audio processing failed: {str(e)}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
def render_puter_tts(text):
    safe_text = json.dumps(text)

    html_code = f"""
    <script src="https://js.puter.com/v2/"></script>

    <div style="background:#1f2937;padding:15px;border-radius:12px;">
        <button id="spark-play"
            style="background:#2563eb;color:white;border:0;
            padding:12px 22px;border-radius:8px;
            cursor:pointer;font-size:15px;">
            ▶ Play SPARK Voice
        </button>

        <span id="spark-status"
            style="color:#d1d5db;margin-left:12px;">
            Ready
        </span>
    </div>

    <script>
        const text = {safe_text};
        const button = document.getElementById("spark-play");
        const status = document.getElementById("spark-status");

        button.addEventListener("click", async () => {{
            button.disabled = true;
            status.textContent = "Generating voice...";

            try {{
                const audio = await puter.ai.txt2speech(text, {{
                    provider: "xai",
                    voice: "leo",
                    language: "en"
                }});

                status.textContent = "Playing SPARK...";
                await audio.play();

                audio.onended = () => {{
                    status.textContent = "Finished";
                    button.disabled = false;
                }};
            }} catch (error) {{
                status.textContent = "Error: " + error.message;
                button.disabled = false;
            }}
        }});
    </script>
    """

    components.html(html_code, height=90)

def main():

    st.set_page_config(
        page_title="SPARK AI",
        page_icon="🎙️",
        layout="centered"
    )

    initialize_session()

    # Interface styling.
    st.markdown("""
        <style>
        .stApp {
            background-color: #0d0d0d;
        }

        .block-container {
            max-width: 900px;
            padding-top: 2rem;
        }

        h1 {
            color: #f3f4f6;
            text-align: center;
        }

        .stChatMessage {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
        }

        .stButton button {
            border-radius: 10px;
            min-height: 42px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h1>🎙️ SPARK AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:#9ca3af;'>"
        "Your personal AI voice assistant"
        "</p>",
        unsafe_allow_html=True
    )

    st.divider()

    # Provider status.
    col1, col2, col3 = st.columns(3)

    col1.metric("Transcription", "Groq Whisper")
    col2.metric("AI Response", "Groq")
    col3.metric("Voice", "Puter.js · xAI")

    st.divider()

    # Display conversation.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Display the latest generated voice response.
    if st.session_state.get("latest_tts_text"):
        render_puter_tts(st.session_state.latest_tts_text)

    # Browser-based microphone input.
    recorded_audio = st.audio_input(
        "Record your message",
        key="spark_microphone"
    )

    if recorded_audio is not None:
        audio_hash = hashlib.sha256(
            recorded_audio.getvalue()
        ).hexdigest()

        if audio_hash != st.session_state.last_audio_hash:
            process_recording(recorded_audio)
            st.rerun()

    # Text-based chat input.
    typed_message = st.chat_input("Type your message...")

    if typed_message:
        process_user_input(typed_message)
        st.rerun()


if __name__ == "__main__":
    main()
