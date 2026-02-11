from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import tempfile
import os
import logging

from app.utils.audio import load_audio_from_bytes, load_audio_from_file, get_audio_duration, validate_audio
from app.utils.text import normalize_indic_text
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# This will be set in main.py
stt_engine = None

def set_engine(engine):
    global stt_engine
    stt_engine = engine

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("hi"),
    decoding: str = Form("ctc"),
    normalize: bool = Form(False)
):
    """
    Transcribe audio file
    
    - audio: Audio file (wav, mp3, ogg, flac, m4a, mpeg, webm)
    - language: Language code (hi, bn, ta, te, mr, gu, kn, ml, pa, or, as)
    - decoding: Decoding mode (ctc or rnnt)
    - normalize: Apply text normalization
    """
    
    if not stt_engine or not stt_engine.loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Please check server logs.")
    
    # Validate inputs
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate language
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Use one of: {', '.join(settings.SUPPORTED_LANGUAGES)}"
        )
    
    # Validate decoding mode (only for ONNX models)
    if stt_engine.model_type == "onnx" and decoding not in settings.DECODING_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decoding mode. Use 'ctc' or 'rnnt'"
        )
    
    # Get file extension
    filename = audio.filename.lower()
    file_ext = filename.split('.')[-1] if '.' in filename else 'wav'
    
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Read audio bytes
        audio_bytes = await audio.read()
        
        # Check file size
        if len(audio_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Convert to tensor
        audio_tensor = load_audio_from_bytes(audio_bytes, file_ext)
        
        # Validate audio
        validate_audio(audio_tensor)
        
        # Log transcription attempt
        logger.info(f"Transcribing {filename} in {language} using {stt_engine.model_type} model")
        
        # Transcribe
        result = stt_engine.transcribe(
            audio_tensor=audio_tensor,
            lang=language,
            decoding=decoding if stt_engine.model_type == "onnx" else "ctc"
        )
        
        # Apply normalization if requested
        if normalize:
            result["normalized_text"] = normalize_indic_text(result["text"], language)
        
        return {
            "success": True,
            "filename": audio.filename,
            "language": language,
            "decoding": decoding if stt_engine.model_type == "onnx" else "default",
            "model_type": stt_engine.model_type,
            **result
        }
        
    except ValueError as e:
        logger.error(f"Validation error for {filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Transcription failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/transcribe/batch")
async def batch_transcribe(
    files: list[UploadFile] = File(...),
    language: str = Form("hi"),
    decoding: str = Form("ctc")
):
    """Transcribe multiple audio files"""
    
    if not stt_engine or not stt_engine.loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 files per batch")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    successful = 0
    failed = 0
    
    for audio_file in files:
        if not audio_file.filename:
            results.append({
                "filename": "unknown",
                "status": "failed",
                "error": "No filename provided"
            })
            failed += 1
            continue
            
        try:
            # Get file extension
            file_ext = audio_file.filename.split('.')[-1].lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise ValueError(f"Unsupported format: {file_ext}")
            
            # Read and process audio
            audio_bytes = await audio_file.read()
            if len(audio_bytes) > settings.MAX_FILE_SIZE:
                raise ValueError("File too large")
            
            audio_tensor = load_audio_from_bytes(audio_bytes, file_ext)
            validate_audio(audio_tensor)
            
            # Transcribe
            result = stt_engine.transcribe(
                audio_tensor=audio_tensor,
                lang=language,
                decoding=decoding if stt_engine.model_type == "onnx" else "ctc"
            )
            
            results.append({
                "filename": audio_file.filename,
                "status": "success",
                "model_type": stt_engine.model_type,
                **result
            })
            successful += 1
            
        except Exception as e:
            logger.error(f"Batch transcription failed for {audio_file.filename}: {e}")
            results.append({
                "filename": audio_file.filename,
                "status": "failed",
                "error": str(e)
            })
            failed += 1
    
    return {
        "total": len(files),
        "successful": successful,
        "failed": failed,
        "results": results
    }

@router.get("/stats")
async def get_stats():
    """Get model performance statistics"""
    
    if not stt_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if not stt_engine.loaded:
        return {
            "status": "not_loaded",
            "message": "Model not loaded yet"
        }
    
    stats = stt_engine.get_stats()
    stats["status"] = "loaded"
    stats["model_type"] = stt_engine.model_type
    
    return stats

@router.get("/languages")
async def list_languages():
    """List supported languages and model info"""
    
    model_info = {
        "languages": settings.SUPPORTED_LANGUAGES,
        "decoding_modes": settings.DECODING_MODES,
        "default_decoding": settings.DEFAULT_DECODING,
        "max_file_size_mb": settings.MAX_FILE_SIZE / 1024 / 1024,
        "allowed_formats": settings.ALLOWED_EXTENSIONS
    }
    
    if stt_engine and stt_engine.loaded:
        model_info["model_status"] = "loaded"
        model_info["model_type"] = stt_engine.model_type
    else:
        model_info["model_status"] = "loading" if stt_engine else "not_initialized"
    
    return model_info