import io
import wave
from pathlib import Path

from piper.voice import PiperVoice

# Voice model path (downloaded on first use)
VOICE_MODEL = Path(__file__).parent / "voices" / "en_US-ryan-medium.onnx"

_voice = None


def get_voice():
    """Lazy-load the voice model."""
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(str(VOICE_MODEL))
    return _voice


def synthesize(text: str) -> bytes:
    """Convert text to WAV audio bytes."""
    voice = get_voice()

    # Synthesize to in-memory WAV
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(voice.config.sample_rate)

        for chunk in voice.synthesize(text):
            wav_file.writeframes(chunk.audio_int16_bytes)

    return buffer.getvalue()
