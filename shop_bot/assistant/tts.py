import io
import urllib.request
import wave
from pathlib import Path

from piper.voice import PiperVoice

# Voice model configuration
VOICE_NAME = "en_US-ryan-high"  # Options: medium, high, low
VOICES_DIR = Path(__file__).parent / "voices"
VOICE_MODEL = VOICES_DIR / f"{VOICE_NAME}.onnx"
VOICE_CONFIG = VOICES_DIR / f"{VOICE_NAME}.onnx.json"

# Hugging Face URL pattern for Piper voices
HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

_voice = None


def download_voice():
    """Download voice model files if they don't exist."""
    VOICES_DIR.mkdir(parents=True, exist_ok=True)

    # Parse voice name: en_US-ryan-high -> en/en_US/ryan/high
    parts = VOICE_NAME.replace("-", "_").split("_")  # ['en', 'US', 'ryan', 'high']
    lang = parts[0]  # en
    locale = f"{parts[0]}_{parts[1]}"  # en_US
    speaker = parts[2]  # ryan
    quality = parts[3]  # high

    base_url = f"{HF_BASE}/{lang}/{locale}/{speaker}/{quality}/{VOICE_NAME}"

    for filepath, url in [(VOICE_MODEL, f"{base_url}.onnx"),
                          (VOICE_CONFIG, f"{base_url}.onnx.json")]:
        if not filepath.exists():
            print(f"Downloading {filepath.name}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded {filepath.name}")


def get_voice():
    """Lazy-load the voice model, downloading if needed."""
    global _voice
    if _voice is None:
        if not VOICE_MODEL.exists() or not VOICE_CONFIG.exists():
            download_voice()
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
