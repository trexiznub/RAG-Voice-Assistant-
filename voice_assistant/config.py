
import os
from dotenv import load_dotenv

# Load local environment variables for development
load_dotenv()


def get_secret(name, default=None):
    """
    Read credentials from Streamlit Secrets first,
    then fall back to local environment variables.
    """
    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    return os.getenv(name, default)


class Config:
    """Application configuration."""

    # Default cloud-compatible providers
    TRANSCRIPTION_MODEL = "groq"
    RESPONSE_MODEL = "groq"
    TTS_MODEL = "elevenlabs"

    # Model selection
    OLLAMA_LLM = "llama3:8b"
    GROQ_LLM = "openai/gpt-oss-20b"
    OPENAI_LLM = "gpt-4o"

    # API credentials
    OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    DEEPGRAM_API_KEY = get_secret("DEEPGRAM_API_KEY")
    ELEVENLABS_API_KEY = get_secret("ELEVENLABS_API_KEY")
    CARTESIA_API_KEY = get_secret("CARTESIA_API_KEY")

    # Local model configuration
    LOCAL_MODEL_PATH = get_secret("LOCAL_MODEL_PATH")

    # Local TTS service
    TTS_PORT_LOCAL = 5150

    # Audio input path
    INPUT_AUDIO = "test.mp3"

    @staticmethod
    def validate_config():
        """Validate selected providers and their API credentials."""

        valid_transcription = [
            "openai", "groq", "deepgram",
            "fastwhisperapi", "local"
        ]

        valid_response = [
            "openai", "groq", "ollama", "local"
        ]

        valid_tts = [
            "openai", "deepgram", "elevenlabs",
            "melotts", "cartesia", "local"
        ]

        if Config.TRANSCRIPTION_MODEL not in valid_transcription:
            raise ValueError("Invalid transcription provider.")

        if Config.RESPONSE_MODEL not in valid_response:
            raise ValueError("Invalid response provider.")

        if Config.TTS_MODEL not in valid_tts:
            raise ValueError("Invalid TTS provider.")

        required_keys = {
            "openai": Config.OPENAI_API_KEY,
            "groq": Config.GROQ_API_KEY,
            "deepgram": Config.DEEPGRAM_API_KEY,
            "elevenlabs": Config.ELEVENLABS_API_KEY,
            "cartesia": Config.CARTESIA_API_KEY,
        }

        selected_providers = [
            Config.TRANSCRIPTION_MODEL,
            Config.RESPONSE_MODEL,
            Config.TTS_MODEL,
        ]

        for provider in selected_providers:
            if provider in required_keys and not required_keys[provider]:
                raise ValueError(
                    f"API key for {provider} is missing."
                )
