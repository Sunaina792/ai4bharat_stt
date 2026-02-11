import os
from pathlib import Path

class Settings:
    PROJECT_NAME = "AI4Bharat STT API"
    VERSION = "1.0.0"
    
    BASE_DIR = Path(__file__).parent.parent
    MODEL_DIR = BASE_DIR / "indic_conformer_model"
    
    # Audio settings
    SAMPLE_RATE = 16000
    AUDIO_DTYPE = "float32"
    
    # Supported languages
    SUPPORTED_LANGUAGES = [
        "hi",  # Hindi
        "bn",  # Bengali
        "ta",  # Tamil
        "te",  # Telugu
        "mr",  # Marathi
        "gu",  # Gujarati
        "kn",  # Kannada
        "ml",  # Malayalam
        "pa",  # Punjabi
        "or",  # Odia
        "as"   # Assamese
    ]
    
    # Decoding modes
    DECODING_MODES = ["ctc", "rnnt"]
    DEFAULT_DECODING = "ctc"  # faster
    
    # API settings
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = ["wav", "mp3", "ogg", "flac", "m4a", "mpeg", "webm"]
    
    # CORS
    CORS_ORIGINS = ["*"]
    
    # Device
    USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"

settings = Settings()