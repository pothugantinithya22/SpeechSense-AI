import os
import sys
import torch
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.hubert_pipeline import decode_speech_audio, VOCAB_SIZE, HuBERTPhonemeModel

def test_hubert_architecture():
    # Mock backbone
    class DummyBackbone(torch.nn.Module):
        def __init__(self):
            super().__init__()
            class Config:
                hidden_size = 768
            self.config = Config()
        def forward(self, x, attention_mask=None):
            class Out:
                last_hidden_state = torch.zeros(x.shape[0], 50, 768)
            return Out()

    dummy = DummyBackbone()
    model = HuBERTPhonemeModel(dummy, VOCAB_SIZE)
    dummy_input = torch.zeros(1, 16000)
    out = model(dummy_input)
    assert out.shape == (1, 50, VOCAB_SIZE)

def test_decode_speech_audio():
    t = torch.arange(16000) / 16000.0
    waveform = 0.5 * torch.sin(2 * 3.14159 * 220 * t)   # non-silent test tone
    detected, confidences = decode_speech_audio(waveform, target_word="rabbit")
    assert isinstance(detected, list)
    assert len(detected) > 0
    assert isinstance(confidences, list)
    assert len(confidences) == len(detected)
    assert all(0.0 <= c <= 1.0 for c in confidences)


def test_silence_returns_no_phonemes():
    detected, confidences = decode_speech_audio(torch.zeros(16000), target_word="rabbit")
    assert detected == [] and confidences == []
