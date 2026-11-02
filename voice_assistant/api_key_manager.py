
from voice_assistant.config import Config


def get_transcription_api_key():
    """Return the API key for the selected transcription provider."""

    providers = {
        "openai": Config.OPENAI_API_KEY,
        "groq": Config.GROQ_API_KEY,
        "deepgram": Config.DEEPGRAM_API_KEY,
    }

    return providers.get(Config.TRANSCRIPTION_MODEL)


def get_response_api_key():
    """Return the API key for the selected response provider."""

    providers = {
        "openai": Config.OPENAI_API_KEY,
        "groq": Config.GROQ_API_KEY,
    }

    return providers.get(Config.RESPONSE_MODEL)


def get_tts_api_key():
    """Return the API key for the selected text-to-speech provider."""

    providers = {
        "openai": Config.OPENAI_API_KEY,
        "deepgram": Config.DEEPGRAM_API_KEY,
        "elevenlabs": Config.ELEVENLABS_API_KEY,
        "cartesia": Config.CARTESIA_API_KEY,
    }

    return providers.get(Config.TTS_MODEL)
