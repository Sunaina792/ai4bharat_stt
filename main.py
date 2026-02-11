from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as stt_router

app = FastAPI(title="Real-time STT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stt_router)

@app.get("/")
async def root():
    return {"message": "Real-time STT API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}