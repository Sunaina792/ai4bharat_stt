from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.config import settings
from app.models.ai4bharat_stt import STTEngine
from app.api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global engine instance
engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global engine
    logger.info("🚀 Starting STT service...")
    
    try:
        engine = STTEngine(str(settings.MODEL_DIR))
        engine.load_model()
        
        # Set engine in routes
        routes.set_engine(engine)
        
        logger.info("✅ Service ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize service: {e}")
        # Continue running but with limited functionality
        logger.info("Service running in limited mode - API endpoints available but transcription may fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down STT service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Real-time Speech-to-Text API for Indic languages with ONNX and HuggingFace fallback support",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router, prefix="/api/v1", tags=["STT"])

@app.get("/")
async def root():
    model_status = "not_loaded"
    model_type = "unknown"
    
    if engine:
        model_status = "loaded" if engine.loaded else "loading"
        model_type = engine.model_type if engine.model_type else "unknown"
    
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "model_status": model_status,
        "model_type": model_type,
        "supported_languages": len(settings.SUPPORTED_LANGUAGES),
        "endpoints": {
            "docs": "/docs",
            "transcribe": "/api/v1/transcribe",
            "batch_transcribe": "/api/v1/transcribe/batch",
            "supported_languages": "/api/v1/languages",
            "performance_stats": "/api/v1/stats",
            "health_check": "/health"
        },
        "info": {
            "max_file_size_mb": settings.MAX_FILE_SIZE / 1024 / 1024,
            "supported_formats": settings.ALLOWED_EXTENSIONS
        }
    }

@app.get("/health")
async def health():
    if not engine:
        return {
            "status": "error",
            "message": "Service not initialized",
            "model_loaded": False
        }
    
    return {
        "status": "healthy" if engine.loaded else "initializing",
        "model_loaded": engine.loaded,
        "model_type": engine.model_type if engine.model_type else "unknown",
        "inference_count": len(engine.inference_times) if engine.inference_times else 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )