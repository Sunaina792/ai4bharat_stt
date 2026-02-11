"""
Configuration management for STT application
"""
import os
from typing import Literal
from pathlib import Path
import torch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# PATHS

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models_cache"
TEMP_DIR = BASE_DIR / "temp_audio"
LOGS_DIR = BASE_DIR / "logs"

MODELS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


# DEVICE & COMPUTE

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "int8")  # int8, float16, float32


# MODEL CONFIGURATION

# AI4Bharat Configuration
AI4BHARAT_MODEL_ID = os.getenv(
    "AI4BHARAT_MODEL_ID",
    "ai4bharat/indic-conformer-600m-multilingual"
)
AI4BHARAT_MODEL_DIR = MODELS_DIR / "ai4bharat"
AI4BHARAT_DECODING_DEFAULT = "ctc"  # ctc or rnnt
AI4BHARAT_OPTIONAL = os.getenv("AI4BHARAT_OPTIONAL", "true").lower() == "true"

# Whisper Configuration
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")  # tiny, base, small, medium, large
WHISPER_MODEL_DIR = MODELS_DIR / "whisper"
WHISPER_DEVICE = DEVICE

# SUPPORTED LANGUAGES
INDIC_LANGUAGES = {
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "as": "Assamese",
    "or": "Odia",
    "sa": "Sanskrit",
    "sd": "Sindhi",
    "ne": "Nepali",
    "si": "Sinhala",
    "kok": "Konkani",
    "mai": "Maithili",
    "doi": "Dogri",
    "mni": "Manipuri",
    "brx": "Bodo",
    "sat": "Santali",
}

ENGLISH_LANGUAGES = {
    "en": "English",
}

HINGLISH_LANGUAGES = {"hi", "mr", "ta", "bn"}

# AUDIO CONFIGURATION
SAMPLE_RATE = 16000  # Hz
MONO = True
MAX_AUDIO_LENGTH = 300  # seconds (5 minutes)
MIN_AUDIO_LENGTH = 0.5  # seconds (minimum detectable)

# INFERENCE CONFIGURATION

WHISPER_BEAM_SIZE = 5
BEAM_SIZE_QUICK = 3
CONFIDENCE_THRESHOLD = 0.5
HINGLISH_WORD_RATIO_THRESHOLD = 0.2


# LOGGING CONFIGURATION

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "json"  # json or text

# API CONFIGURATION

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))
API_RELOAD = os.getenv("API_RELOAD", "False").lower() == "true"


# TIMEOUT CONFIGURATION (seconds)

INFERENCE_TIMEOUT = 60
FILE_UPLOAD_MAX_SIZE = 52_428_800  # 50 MB


# ENVIRONMENT

ENV = os.getenv("ENV", "development")  # development or production
DEBUG = ENV == "development"