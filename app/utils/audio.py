
import librosa
import torch
import numpy as np
import soundfile as sf
import io
from pydub import AudioSegment

def load_audio_from_file(file_path: str, target_sr: int = 16000):
    """Load audio file and convert to proper format"""
    audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
    audio = audio.astype(np.float32)
    return torch.from_numpy(audio).unsqueeze(0)

def load_audio_from_bytes(audio_bytes: bytes, source_format: str, target_sr: int = 16000):
    """Convert audio bytes to tensor"""
    
    # Use pydub to handle different formats
    audio_segment = AudioSegment.from_file(
        io.BytesIO(audio_bytes),
        format=source_format
    )
    
    # Convert to mono and target sample rate
    audio_segment = audio_segment.set_channels(1)
    audio_segment = audio_segment.set_frame_rate(target_sr)
    
    # Export to wav bytes
    wav_io = io.BytesIO()
    audio_segment.export(wav_io, format="wav")
    wav_io.seek(0)
    
    # Load with librosa
    audio, sr = librosa.load(wav_io, sr=target_sr, mono=True)
    audio = audio.astype(np.float32)
    
    return torch.from_numpy(audio).unsqueeze(0)

def get_audio_duration(audio_tensor: torch.Tensor, sr: int = 16000):
    """Get audio duration in seconds"""
    return audio_tensor.shape[-1] / sr

def validate_audio(audio_tensor: torch.Tensor, max_duration: int = 300):
    """Check if audio is valid"""
    duration = get_audio_duration(audio_tensor)
    
    if duration > max_duration:
        raise ValueError(f"Audio too long: {duration}s (max: {max_duration}s)")
    
    if duration < 0.1:
        raise ValueError("Audio too short")
    
    return True