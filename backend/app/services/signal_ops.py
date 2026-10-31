"""Dependency-light signal helpers (numpy + scipy only) for the 'Data Preprocessing' stage:
noise reduction (spectral gating) and speech segmentation."""
import numpy as np
from scipy.signal import stft, istft
from scipy.ndimage import uniform_filter1d


def reduce_noise(samples: np.ndarray, sr: int, prop_decrease: float = 0.8) -> np.ndarray:
    """Mild spectral-gating noise reduction. The noise profile is estimated from the
    quietest 15% of frames, so no separate noise recording is needed."""
    if samples.size < sr * 0.3:
        return samples
    nper, hop = 1024, 256
    _, _, spec = stft(samples, fs=sr, nperseg=nper, noverlap=nper - hop)
    mag, phase = np.abs(spec), np.angle(spec)
    energy = mag.sum(axis=0)
    k = max(1, int(0.15 * mag.shape[1]))
    noise = mag[:, np.argsort(energy)[:k]].mean(axis=1, keepdims=True)
    mask = np.clip((mag - 1.5 * noise) / (mag + 1e-8), 0.0, 1.0)
    mask = uniform_filter1d(mask, size=3, axis=1)
    mask = 1.0 - prop_decrease * (1.0 - mask)
    _, cleaned = istft(mag * mask * np.exp(1j * phase), fs=sr, nperseg=nper, noverlap=nper - hop)
    cleaned = cleaned[: len(samples)]
    if len(cleaned) < len(samples):
        cleaned = np.pad(cleaned, (0, len(samples) - len(cleaned)))
    return cleaned.astype(np.float32)


def segment_speech(samples: np.ndarray, sr: int, top_db: float = 30.0, min_gap_sec: float = 0.3):
    """Speech segmentation by frame energy. Returns [{'start': s, 'end': s}] in seconds,
    merging pauses shorter than min_gap_sec."""
    if samples.size == 0:
        return []
    frame, hop = int(0.025 * sr), int(0.010 * sr)
    n = max(1, 1 + (len(samples) - frame) // hop) if len(samples) >= frame else 1
    rms = np.array([np.sqrt(np.mean(samples[i * hop: i * hop + frame] ** 2) + 1e-12) for i in range(n)])
    db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12)
    active = db > -top_db
    segs, start = [], None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            segs.append([start, i]); start = None
    if start is not None:
        segs.append([start, n])
    merged = []
    for s, e in segs:
        if merged and (s - merged[-1][1]) * hop / sr < min_gap_sec:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    return [{"start": round(s * hop / sr, 2), "end": round(min(len(samples), e * hop + frame) / sr, 2)}
            for s, e in merged]
