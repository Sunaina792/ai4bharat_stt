#!/usr/bin/env python3
"""
Test script for the STT backend
"""

import requests
import time
import json
from pathlib import Path

def test_health_check():
    """Test health endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Root status: {response.status_code}")
        data = response.json()
        print(f"Service: {data.get('service')}")
        print(f"Version: {data.get('version')}")
        print(f"Model status: {data.get('model_status')}")
        print(f"Model type: {data.get('model_type')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_languages_endpoint():
    """Test languages endpoint"""
    print("\n🔍 Testing languages endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/languages")
        print(f"Languages status: {response.status_code}")
        data = response.json()
        print(f"Supported languages: {len(data.get('languages', []))}")
        print(f"Model status: {data.get('model_status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Languages endpoint failed: {e}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print("\n🔍 Testing stats endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/stats")
        print(f"Stats status: {response.status_code}")
        data = response.json()
        print(f"Stats: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Stats endpoint failed: {e}")
        return False

def create_test_audio():
    """Create a simple test audio file"""
    try:
        import numpy as np
        import soundfile as sf
        
        # Create 3 seconds of silence (16kHz)
        sample_rate = 16000
        duration = 3
        audio_data = np.zeros(int(sample_rate * duration), dtype=np.float32)
        
        # Save as WAV
        test_file = Path("test_silence.wav")
        sf.write(test_file, audio_data, sample_rate)
        print(f"✅ Created test audio file: {test_file}")
        return str(test_file)
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return None

def test_transcription():
    """Test transcription endpoint with test audio"""
    print("\n🔍 Testing transcription endpoint...")
    
    # Create test audio
    test_file = create_test_audio()
    if not test_file:
        return False
    
    try:
        with open(test_file, 'rb') as f:
            files = {'audio': ('test_silence.wav', f, 'audio/wav')}
            data = {
                'language': 'hi',
                'decoding': 'ctc',
                'normalize': 'false'
            }
            
            print("Sending transcription request...")
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/v1/transcribe",
                files=files,
                data=data
            )
            end_time = time.time()
            
            print(f"Transcription status: {response.status_code}")
            print(f"Response time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Transcription successful!")
                print(f"Text: {result.get('text', 'N/A')}")
                print(f"Confidence: {result.get('confidence', 'N/A')}%")
                print(f"Model type: {result.get('model_type', 'N/A')}")
                return True
            else:
                print(f"❌ Transcription failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return False
    finally:
        # Clean up test file
        try:
            Path(test_file).unlink()
        except:
            pass

def main():
    """Run all tests"""
    print("🧪 Starting STT Backend Tests\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Languages Endpoint", test_languages_endpoint),
        ("Stats Endpoint", test_stats_endpoint),
        ("Transcription", test_transcription)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()