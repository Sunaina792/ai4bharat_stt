import sys
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import Optional, Dict, Tuple
import time
import logging
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STTEngine:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.model = None
        self.config = None
        self.loaded = False
        self.model_type = None  # "onnx" or "transformers_pipeline"
        
        # Performance tracking
        self.inference_times = []
        
        # Initialize fallback transformer model using pipeline
        self.transformer_pipeline = None
        
    def load_model(self):
        """Load the STT model with fallback to transformers"""
        
        # Try loading ONNX model first
        if self._load_onnx_model():
            self.model_type = "onnx"
            logger.info("✅ ONNX model loaded successfully")
            return
        
        # Fallback to transformers model
        logger.info("🔄 ONNX model not found, falling back to transformers model")
        if self._load_transformers_model():
            self.model_type = "transformers"
            logger.info("✅ Transformers model loaded successfully")
            return
        
        raise RuntimeError("Failed to load any model. Please check model files.")
    
    def _load_onnx_model(self) -> bool:
        """Try to load ONNX model"""
        try:
            if not self.model_dir.exists():
                logger.warning(f"Model directory not found: {self.model_dir}")
                return False
            
            # Add model directory to path
            sys.path.insert(0, str(self.model_dir))
            
            from model_onnx import IndicASRConfig, IndicASRModel
            
            self.config = IndicASRConfig(
                ts_folder=str(self.model_dir)
            )
            
            self.model = IndicASRModel(self.config)
            self.model.eval()
            self.loaded = True
            return True
            
        except ImportError as e:
            logger.warning(f"ONNX model modules not found: {e}")
            return False
        except Exception as e:
            logger.warning(f"Failed to load ONNX model: {e}")
            return False
    
    def _load_transformers_model(self) -> bool:
        """Load transformers model as fallback using pipeline"""
        try:
            from transformers import pipeline
            import torch
            
            model_name = "ai4bharat/indic-conformer-600m-multilingual"
            device = 0 if torch.cuda.is_available() else -1
            
            logger.info(f"Loading transformers pipeline: {model_name}, device: {device}")
            
            self.transformer_pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                device=device
            )
            
            self.loaded = True
            return True
            
        except ImportError as e:
            logger.error(f"Transformers library not properly installed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load transformers model: {e}")
            return False
    
    def transcribe(
        self,
        audio_tensor: torch.Tensor,
        lang: str = "hi",
        decoding: str = "ctc"
    ) -> Dict:
        """
        Transcribe audio tensor using available model
        
        Args:
            audio_tensor: Shape (1, T), dtype float32
            lang: Language code (hi, bn, ta, etc.)
            decoding: "ctc" (faster) or "rnnt" (more accurate)
        
        Returns:
            Dict with text, confidence, inference_time, rtf
        """
        
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        try:
            if self.model_type == "onnx":
                result = self._transcribe_with_onnx(audio_tensor, lang, decoding)
            elif self.model_type == "transformers":
                result = self._transcribe_with_transformers(audio_tensor, lang)
            else:
                raise RuntimeError("No model loaded")
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
        
        end_time = time.time()
        inference_time = end_time - start_time
        
        # Calculate RTF (Real Time Factor)
        audio_duration = audio_tensor.shape[-1] / 16000
        rtf = inference_time / audio_duration if audio_duration > 0 else 0
        
        # Track performance
        self.inference_times.append(inference_time)
        
        return {
            "text": result["text"],
            "confidence": result.get("confidence", 85.0),
            "inference_time": round(inference_time, 3),
            "rtf": round(rtf, 3),
            "audio_duration": round(audio_duration, 2),
            "model_type": self.model_type
        }
    
    def _transcribe_with_onnx(self, audio_tensor: torch.Tensor, lang: str, decoding: str) -> Dict:
        """Transcribe using ONNX model"""
        with torch.no_grad():
            text = self.model(
                wav=audio_tensor,
                lang=lang,
                decoding=decoding
            )
        
        # Calculate confidence
        confidence = self._calculate_confidence(audio_tensor, lang)
        
        return {
            "text": text,
            "confidence": round(confidence * 100, 2)
        }
    
    def _transcribe_with_transformers(self, audio_tensor: torch.Tensor, lang: str) -> Dict:
        """Transcribe using transformers pipeline"""
        try:
            import soundfile as sf
            import numpy as np
            import io
            
            # Convert tensor to numpy
            audio_np = audio_tensor.squeeze().numpy()
            
            # Create temporary file for the pipeline
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
                
            try:
                # Write audio to temporary file
                sf.write(temp_filename, audio_np, 16000)
                
                # Use the pipeline for transcription
                result = self.transformer_pipeline(temp_filename)
                
                transcription = result["text"] if isinstance(result, dict) and "text" in result else str(result)
                
                return {
                    "text": transcription,
                    "confidence": 85.0  # Default confidence for transformers pipeline
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    
        except Exception as e:
            logger.error(f"Transformers pipeline transcription failed: {e}")
            raise
    
    def _calculate_confidence(self, wav_input: torch.Tensor, lang: str) -> float:
        """Calculate average token confidence score for ONNX model"""
        
        if self.model_type != "onnx":
            return 0.85  # Default confidence for non-ONNX models
        
        try:
            with torch.no_grad():
                encoder_outputs_np, encoded_lengths_np = self.model.encode(wav=wav_input)
                
                ctc_decoder_session = self.model.models['ctc_decoder']
                raw_logprobs_np = ctc_decoder_session.run(
                    ['logprobs'],
                    {'encoder_output': encoder_outputs_np}
                )[0]
                
                logprobs_tensor = torch.from_numpy(raw_logprobs_np)
                lang_mask_indices = self.model.language_masks[lang]
                
                logits_with_batch_dim = logprobs_tensor[:, :, lang_mask_indices].log_softmax(dim=-1)
                logits = logits_with_batch_dim[0]
            
            probs = F.softmax(logits, dim=-1)
            pred_ids = torch.argmax(probs, dim=-1)
            
            token_confidences = []
            for t, token_id in enumerate(pred_ids):
                token_confidences.append(probs[t, token_id].item())
            
            if len(token_confidences) > 0:
                return sum(token_confidences) / len(token_confidences)
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.85  # Return default confidence on failure
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        
        if not self.inference_times:
            return {
                "total_inferences": 0,
                "model_type": self.model_type or "not_loaded"
            }
        
        return {
            "total_inferences": len(self.inference_times),
            "avg_inference_time": round(sum(self.inference_times) / len(self.inference_times), 3),
            "min_inference_time": round(min(self.inference_times), 3),
            "max_inference_time": round(max(self.inference_times), 3),
            "model_type": self.model_type
        }