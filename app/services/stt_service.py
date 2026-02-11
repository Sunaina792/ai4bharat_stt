import time
from dataclasses import dataclass
from transformers import pipeline
import torch

@dataclass
class TranscriptionResult:
    text: str
    language: str = "hi"
    confidence: float = 0.85
    processing_time: float = 0.0


class AI4BharatSTT:
    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1

        self.asr = pipeline(
            "automatic-speech-recognition",
            model="ai4bharat/indic-conformer-600m-multilingual",
            device=device
        )

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        start = time.time()

        result = self.asr(audio_path)

        return TranscriptionResult(
            text=result["text"],
            processing_time=time.time() - start
        )


# SINGLE GLOBAL INSTANCE
ai4bharat_stt = AI4BharatSTT()
