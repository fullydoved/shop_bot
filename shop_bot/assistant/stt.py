import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

# Model configuration
MODEL_SIZE = "base"
COMPUTE_TYPE = "int8"  # CPU-optimized quantization
MODELS_DIR = Path(__file__).parent / "models"

_model = None


def download_model():
    """Download the Whisper model if it doesn't exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Whisper {MODEL_SIZE} model...")
    # This triggers faster-whisper to download from HuggingFace
    WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE,
                 download_root=str(MODELS_DIR))
    print(f"Downloaded Whisper {MODEL_SIZE} model")


def get_model():
    """Lazy-load the Whisper model, downloading if needed."""
    global _model
    if _model is None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE,
                              download_root=str(MODELS_DIR))
    return _model


def transcribe(audio_bytes: bytes, format_hint: str = "webm") -> str:
    """Transcribe audio bytes to text.

    Args:
        audio_bytes: Raw audio data
        format_hint: File extension hint (webm, wav, ogg)

    Returns:
        Transcribed text
    """
    model = get_model()

    # Write to temp file (faster-whisper requires file path)
    suffix = f".{format_hint}" if format_hint else ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        segments, _ = model.transcribe(temp_path, language="en")
        # Combine all segments into single text
        text = " ".join(segment.text.strip() for segment in segments)
        return text.strip()
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)
