# AI4Bharat Real-time Speech-to-Text API

A production-ready FastAPI backend for real-time speech-to-text transcription of Indic languages with support for both ONNX and HuggingFace transformer models.

## 🌟 Features

- **Multi-language Support**: 11 Indic languages (Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese)
- **Dual Model Support**: ONNX models for production + HuggingFace transformers as fallback
- **Real-time Processing**: Low-latency transcription with performance metrics
- **Batch Processing**: Transcribe multiple files in a single request
- **Comprehensive API**: RESTful endpoints with OpenAPI documentation
- **Robust Error Handling**: Graceful fallbacks and detailed error reporting
- **Performance Monitoring**: Real-time factor (RTF) and confidence scoring

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python start_server.py
```

Or manually:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## 📡 API Endpoints

### Transcribe Audio

```http
POST /api/v1/transcribe
Content-Type: multipart/form-data

audio: <audio_file>
language: hi|bn|ta|te|mr|gu|kn|ml|pa|or|as (default: hi)
decoding: ctc|rnnt (default: ctc)
normalize: true|false (default: false)
```

### Batch Transcription

```http
POST /api/v1/transcribe/batch
Content-Type: multipart/form-data

files: [<audio_file1>, <audio_file2>, ...]
language: hi|bn|ta|te|mr|gu|kn|ml|pa|or|as (default: hi)
decoding: ctc|rnnt (default: ctc)
```

### Get Supported Languages

```http
GET /api/v1/languages
```

### Get Performance Statistics

```http
GET /api/v1/stats
```

## 🧪 Testing

Run the test suite:

```bash
python test_backend.py
```

## 📁 Project Structure

```
REALTIME_STT/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── models/
│   │   └── ai4bharat_stt.py   # STT engine with dual model support
│   ├── services/
│   │   ├── infer.py           # Legacy inference code
│   │   └── stt_service.py     # Alternative STT service
│   ├── utils/
│   │   ├── audio.py           # Audio processing utilities
│   │   └── text.py            # Text processing utilities
│   ├── config.py              # Application configuration
│   └── main.py                # FastAPI application
├── indic_conformer_model/     # ONNX model directory (optional)
├── requirements.txt           # Python dependencies
├── start_server.py            # Startup script
├── test_backend.py            # Test suite
└── README.md
```

## ⚙️ Configuration

Key configuration options in `app/config.py`:

- `SUPPORTED_LANGUAGES`: List of supported language codes
- `DECODING_MODES`: Available decoding modes (CTC, RNN-T)
- `MAX_FILE_SIZE`: Maximum upload size (50MB default)
- `ALLOWED_EXTENSIONS`: Supported audio formats
- `USE_GPU`: Enable/disable GPU usage

## 🔧 Model Support

### ONNX Model (Primary)

Place your ONNX model files in `indic_conformer_model/` directory with:
- `model_onnx.py`
- Required ONNX model files

### Transformers Model (Fallback)

Automatically uses `ai4bharat/indic-conformer-600m-multilingual` from HuggingFace when ONNX model is not available.

## 📊 Performance Metrics

The API returns detailed performance information:

- **Text**: Transcribed text
- **Confidence**: Confidence score (0-100%)
- **Inference Time**: Processing time in seconds
- **RTF**: Real Time Factor (inference_time / audio_duration)
- **Audio Duration**: Length of input audio
- **Model Type**: Which model was used (onnx/transformers)

## 🛠️ Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Code Quality

```bash
flake8 app/
black app/
mypy app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [AI4Bharat](https://ai4bharat.org/) for the Indic language models
- FastAPI for the web framework
- HuggingFace for transformer models



