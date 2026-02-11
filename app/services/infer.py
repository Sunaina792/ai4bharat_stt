import torch
import librosa
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

MODEL_NAME = "ai4bharat/indic_conformer_models"

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_NAME)
model.to(device)
model.eval()


def transcribe_audio(audio_path: str):
    speech, sr = librosa.load(audio_path, sr=16000)

    inputs = processor(
        speech,
        sampling_rate=16000,
        return_tensors="pt"
    )

    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_features"].to(device),
            max_length=256
        )

    transcription = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    return transcription
