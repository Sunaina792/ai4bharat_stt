"""
Custom exception classes for the STT application
"""

class STTException(Exception):
    """Base exception for STT application"""
    pass

class ModelException(STTException):
    """Exception related to model loading or inference"""
    pass

class AudioException(STTException):
    """Exception related to audio processing"""
    pass

class LanguageException(STTException):
    """Exception related to language support"""
    pass