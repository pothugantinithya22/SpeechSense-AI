import io
import os
import wave
import struct
import numpy as np
import torch
import torchaudio
import soundfile as sf
import librosa
from app.config import SAMPLE_RATE, MAX_AUDIO_DURATION_SEC

def decode_audio_bytes(data: bytes) -> tuple[torch.Tensor, int]:
    """
    Decodes audio bytes through multi-stage robust fallback:
    1. soundfile (WAV, FLAC, OGG)
    2. python standard wave module (for standard WAV)
    3. torchaudio.load
    4. librosa.load
    """
    # 1. soundfile
    try:
        samples, sr = sf.read(io.BytesIO(data), dtype="float32")
        if isinstance(samples, np.ndarray):
            if samples.ndim == 1:
                waveform = torch.tensor(samples).unsqueeze(0)
            else:
                # [channels, time]
                waveform = torch.tensor(samples.T)
            return waveform, sr
    except Exception:
        pass

    # 2. Python wave module fallback
    try:
        with wave.open(io.BytesIO(data), "rb") as wf:
            channels = wf.getnchannels()
            sr = wf.getframerate()
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
            sampwidth = wf.getsampwidth()
            if sampwidth == 2:
                arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                if channels > 1:
                    arr = arr.reshape(-1, channels).T
                else:
                    arr = arr.reshape(1, -1)
                return torch.tensor(arr, dtype=torch.float32), sr
    except Exception:
        pass

    # 3. torchaudio
    try:
        waveform, sr = torchaudio.load(io.BytesIO(data))
        return waveform, sr
    except Exception:
        pass

    # 4. librosa
    try:
        samples, sr = librosa.load(io.BytesIO(data), sr=None, mono=False)
        if isinstance(samples, np.ndarray):
            if samples.ndim == 1:
                samples = np.expand_dims(samples, axis=0)
            return torch.tensor(samples, dtype=torch.float32), sr
    except Exception:
        pass

    raise RuntimeError("Unable to decode audio format. Please provide valid WAV, MP3, or OGG audio.")

def preprocess_audio_detailed(data: bytes, target_sr: int = SAMPLE_RATE):
    """
    Data-preprocessing stage of the SpeechSense pipeline. Returns (waveform, info).
      decode -> mono -> resample 16 kHz -> noise reduction -> trim silence
      -> speech segmentation -> peak normalisation -> duration cap
    """
    from app.services.signal_ops import reduce_noise, segment_speech
    waveform, sr = decode_audio_bytes(data)
    info = {"original_sample_rate": int(sr), "sample_rate": target_sr}

    if waveform.ndim > 1 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    elif waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)

    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)
        waveform = resampler(waveform)
        info["resampled"] = True
    else:
        info["resampled"] = False

    samples = waveform.squeeze(0).numpy().astype(np.float32)

    # Noise reduction (spectral gating); disable with NOISE_REDUCTION=0 in backend/.env
    info["noise_reduced"] = False
    if os.getenv("NOISE_REDUCTION", "1") == "1":
        try:
            samples = reduce_noise(samples, target_sr)
            info["noise_reduced"] = True
        except Exception:
            pass

    # Trim leading/trailing silence
    try:
        trimmed_samples, _ = librosa.effects.trim(samples, top_db=35)
        if len(trimmed_samples) > target_sr * 0.15:
            samples = trimmed_samples
    except Exception:
        pass

    max_amp = np.max(np.abs(samples)) if samples.size else 0.0
    if max_amp > 1e-5:
        samples = samples / max_amp * 0.95

    max_samples = int(MAX_AUDIO_DURATION_SEC * target_sr)
    if len(samples) > max_samples:
        samples = samples[:max_samples]
        info["truncated"] = True

    # Speech segmentation (words / phrases separated by pauses)
    try:
        info["segments"] = segment_speech(samples, target_sr)
    except Exception:
        info["segments"] = []
    info["duration_sec"] = round(len(samples) / target_sr, 2)
    return torch.tensor(samples, dtype=torch.float32), info


def preprocess_audio(data: bytes, target_sr: int = SAMPLE_RATE) -> torch.Tensor:
    """Backwards-compatible wrapper: returns only the cleaned waveform."""
    return preprocess_audio_detailed(data, target_sr)[0]

def tensor_to_wav_bytes(waveform: torch.Tensor, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Converts a 1D or 2D tensor to standard WAV file bytes."""
    if waveform.ndim > 1:
        waveform = waveform.squeeze(0)
    samples = waveform.numpy().astype(np.float32)
    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.read()
