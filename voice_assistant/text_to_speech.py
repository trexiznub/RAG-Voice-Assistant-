import asyncio
import edge_tts


def text_to_speech(model, api_key, text, output_file_path, local_model_path=None):
    """
    Generate speech using Microsoft Edge TTS.
    No API key is required.
    """

    async def generate_audio():
        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-ChristopherNeural",
            rate="-5%",
            volume="+0%",
        )
        await communicate.save(output_file_path)

    asyncio.run(generate_audio())
    return output_file_path