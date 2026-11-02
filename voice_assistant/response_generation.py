
import logging
from openai import OpenAI
from groq import Groq

from voice_assistant.config import Config


def generate_response(
    model: str,
    api_key: str,
    chat_history: list,
    local_model_path: str = None
):
    """Generate a response using the selected cloud LLM."""

    try:
        if model == "openai":
            return _generate_openai_response(api_key, chat_history)

        elif model == "groq":
            return _generate_groq_response(api_key, chat_history)

        else:
            raise ValueError(
                f"Unsupported cloud response model: {model}"
            )

    except Exception:
        logging.exception("Failed to generate AI response")
        raise


def _generate_openai_response(api_key, chat_history):
    if not api_key:
        raise ValueError("OpenAI API key is missing.")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=Config.OPENAI_LLM,
        messages=chat_history
    )

    return response.choices[0].message.content


def _generate_groq_response(api_key, chat_history):
    if not api_key:
        raise ValueError("Groq API key is missing.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=Config.GROQ_LLM,
        messages=chat_history
    )

    return response.choices[0].message.content
