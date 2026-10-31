import os
import sys
import torch
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.audio_preprocessor import preprocess_audio, tensor_to_wav_bytes
from app.config import SAMPLE_RATE

def test_preprocess_synthetic_audio():
    # Create 1 second synthetic sine wave tensor
    duration = 1.0
    sr = 8000 # Non-16k to test resampling
    t = torch.linspace(0, duration, int(sr * duration))
    synthetic = torch.sin(2 * 3.14159 * 440 * t).unsqueeze(0)

    # Convert to WAV bytes
    wav_bytes = tensor_to_wav_bytes(synthetic, sample_rate=sr)
    assert len(wav_bytes) > 0

    # Preprocess
    processed = preprocess_audio(wav_bytes, target_sr=SAMPLE_RATE)
    assert isinstance(processed, torch.Tensor)
    assert processed.ndim == 1
    # Check that it was resampled close to 16000 samples
    assert abs(len(processed) - SAMPLE_RATE) < 2000
    # Check peak normalization <= 1.0
    assert torch.max(torch.abs(processed)).item() <= 0.96

def test_preprocess_demo_file():
    demo_path = os.path.join(os.path.dirname(__file__), "..", "data", "demo_audio", "rabbit_sample.wav")
    if os.path.exists(demo_path):
        with open(demo_path, "rb") as f:
            data = f.read()
        processed = preprocess_audio(data)
        assert isinstance(processed, torch.Tensor)
        assert len(processed) > 1000
