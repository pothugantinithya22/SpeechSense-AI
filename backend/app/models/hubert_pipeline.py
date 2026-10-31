"""
HuBERT acoustic phoneme recognition pipeline for SpeechSense.

Three modes are tried in order, and the active one is ALWAYS reported to the caller:

  1. "hubert_phoneme"  - your trained HuBERT + CTC phoneme checkpoint (best_cmu_93.2pct.pt).
                         Reads real phonemes straight from the audio.
  2. "hubert_asr"      - facebook/hubert-large-ls960-ft speech recognition. The audio is
                         transcribed and the transcript converted to CMU phonemes.
                         Reflects what was really said (word level).
  3. "demo_fallback"   - offline heuristic for demos only. It does NOT recognise speech.
                         Results are labelled as demo data.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

from app.config import (
    HF_MODEL_REPO, HF_MODEL_FILE, HF_MODEL_PATH, MODEL_DIR, HF_HUBERT_MODEL,
    DEVICE, SAMPLE_RATE, ENABLE_HF_DOWNLOAD, OFFLINE, ALLOW_DEMO_FALLBACK,
)
from app.services.alignment import CMU_PHONEMES, PHONE_SET, word_to_phonemes
from app.services.label_utils import extract_labels, to_phoneme

PHONEMES = list(CMU_PHONEMES)
PHONE_TO_INDEX = {phone: idx for idx, phone in enumerate(PHONEMES)}
PHONE_TO_INDEX["<blank>"] = len(PHONE_TO_INDEX)
INDEX_TO_PHONE = {idx: phone for phone, idx in PHONE_TO_INDEX.items()}
BLANK_INDEX = PHONE_TO_INDEX["<blank>"]
VOCAB_SIZE = len(PHONE_TO_INDEX)
MIN_RUN_FRAMES = 2     # ignore 1-frame (20 ms) flickers
MIN_RUN_CONF = 0.45    # ignore low-confidence phonemes


class HuBERTPhonemeModel(nn.Module):
    """HuBERT backbone with a CTC linear projection head for CMU phoneme classification."""

    def __init__(self, hubert_backbone, vocab_size: int = VOCAB_SIZE):
        super().__init__()
        self.hubert = hubert_backbone
        hidden_size = getattr(hubert_backbone.config, "hidden_size", 768)

        try:
            if hasattr(self.hubert, "feature_extractor"):
                self.hubert.feature_extractor._freeze_parameters()
        except Exception:
            pass

        self.projection = nn.Sequential(
            nn.Linear(hidden_size, 512),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(512, vocab_size),
        )

    def forward(self, input_values, attention_mask=None):
        hidden = self.hubert(input_values, attention_mask=attention_mask).last_hidden_state
        return self.projection(hidden)


# --------------------------------------------------------------------------------------
# Global state
# --------------------------------------------------------------------------------------
_PHONEME_MODEL = None
_LABELS = [INDEX_TO_PHONE[i] for i in range(VOCAB_SIZE)]   # class index -> phoneme (replaced from the checkpoint when known)
_BLANK_IDX = BLANK_INDEX
_PHONEME_EXTRACTOR = None
_ASR_MODEL = None
_ASR_PROCESSOR = None
_INITIALIZED = False
_STATUS = {
    "mode": "not_loaded",
    "checkpoint": None,
    "messages": [],
}


def _log(msg: str):
    print(f"[SpeechSense] {msg}")
    _STATUS["messages"].append(msg)


def _find_checkpoint():
    """Look for the trained checkpoint in every sensible place; download it if allowed."""
    candidates = [
        Path(HF_MODEL_PATH),
        Path.cwd() / HF_MODEL_FILE,
        Path.cwd() / "models" / HF_MODEL_FILE,
        Path.cwd().parent / "models" / HF_MODEL_FILE,
    ]
    for c in candidates:
        if c.is_file():
            return str(c)

    if ENABLE_HF_DOWNLOAD and not OFFLINE:
        try:
            from huggingface_hub import hf_hub_download
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            _log(f"Downloading checkpoint {HF_MODEL_FILE} from {HF_MODEL_REPO} ...")
            path = hf_hub_download(repo_id=HF_MODEL_REPO, filename=HF_MODEL_FILE, local_dir=str(MODEL_DIR))
            return path
        except Exception as exc:
            _log(f"Checkpoint download failed: {exc}")
    else:
        _log("Checkpoint not found locally and downloading is disabled/offline.")
    return None


def _load_phoneme_model():
    global _PHONEME_MODEL, _PHONEME_EXTRACTOR
    ckpt_path = _find_checkpoint()
    if not ckpt_path:
        return False
    try:
        from transformers import HubertModel, Wav2Vec2FeatureExtractor
        local_only = OFFLINE
        extractor = Wav2Vec2FeatureExtractor.from_pretrained(HF_HUBERT_MODEL, local_files_only=local_only)
        backbone = HubertModel.from_pretrained(HF_HUBERT_MODEL, local_files_only=local_only)

        checkpoint = torch.load(ckpt_path, map_location=DEVICE, weights_only=False)
        state_dict = checkpoint
        if isinstance(checkpoint, dict):
            for key in ("model", "model_state_dict", "state_dict"):
                if key in checkpoint and isinstance(checkpoint[key], dict):
                    state_dict = checkpoint[key]
                    break
        state_dict = {k.replace("module.", "", 1): v for k, v in state_dict.items()}

        # Infer the real output size from the checkpoint instead of assuming 40.
        out_keys = [k for k in state_dict if k.startswith("projection.") and k.endswith("weight")]
        vocab = VOCAB_SIZE
        if out_keys:
            last = sorted(out_keys, key=lambda k: int(k.split(".")[1]))[-1]
            vocab = state_dict[last].shape[0]
        # Work out which phoneme each output class means (never guess silently).
        global _LABELS, _BLANK_IDX
        labels, blank, src = extract_labels(checkpoint, vocab, MODEL_DIR / "phoneme_labels.json")
        if labels:
            _LABELS, _BLANK_IDX = labels, blank
            _log(f"Phoneme labels read from {src}: {vocab} classes, blank index {blank}.")
        elif vocab == VOCAB_SIZE:
            _log("Checkpoint has 40 classes: using the standard alphabetical CMU labels + blank last.")
        else:
            msg = (f"Checkpoint has {vocab} output classes but the code expects {VOCAB_SIZE}, and its label "
                   f"order is unknown ({src}). Run 'python inspect_checkpoint.py', or create "
                   f"models/phoneme_labels.json with the label list used during training.")
            if os.getenv("FORCE_PHONEME_MODEL", "0") == "1":
                _log("WARNING: " + msg + " Continuing anyway because FORCE_PHONEME_MODEL=1 - labels may be WRONG.")
                _LABELS = (PHONEMES + ["<blank>"] * vocab)[: vocab - 1] + ["<blank>"]
                _BLANK_IDX = vocab - 1
            else:
                _log("Not using the phoneme checkpoint: " + msg)
                return False

        model = HuBERTPhonemeModel(backbone, vocab)
        result = model.load_state_dict(state_dict, strict=False)
        n_total = len(list(model.state_dict().keys()))
        n_missing = len(result.missing_keys)
        _log(f"Checkpoint loaded: {n_total - n_missing}/{n_total} tensors matched "
             f"({len(result.unexpected_keys)} unexpected).")

        # If the projection head did not load, the model outputs random noise -> reject it.
        if any(k.startswith("projection.") for k in result.missing_keys):
            _log("Checkpoint does NOT match the projection head - not using it.")
            return False

        model.to(DEVICE).eval()
        _PHONEME_MODEL, _PHONEME_EXTRACTOR = model, extractor
        _STATUS["checkpoint"] = ckpt_path
        return True
    except Exception as exc:
        _log(f"Could not load phoneme checkpoint: {exc}")
        return False


def _load_asr_model():
    global _ASR_MODEL, _ASR_PROCESSOR
    try:
        from transformers import HubertForCTC, Wav2Vec2Processor
        local_only = OFFLINE
        _ASR_PROCESSOR = Wav2Vec2Processor.from_pretrained(HF_HUBERT_MODEL, local_files_only=local_only)
        _ASR_MODEL = HubertForCTC.from_pretrained(HF_HUBERT_MODEL, local_files_only=local_only).to(DEVICE).eval()
        return True
    except Exception as exc:
        _log(f"Could not load HuBERT speech recogniser: {exc}")
        return False


def load_hubert_pipeline():
    """Load models once. Returns (phoneme_model, extractor) for backwards compatibility."""
    global _INITIALIZED
    if _INITIALIZED:
        return _PHONEME_MODEL, _PHONEME_EXTRACTOR

    if _load_phoneme_model():
        _STATUS["mode"] = "hubert_phoneme"
    elif _load_asr_model():
        _STATUS["mode"] = "hubert_asr"
    else:
        _STATUS["mode"] = "demo_fallback" if ALLOW_DEMO_FALLBACK else "unavailable"
    _log(f"Active mode: {_STATUS['mode']}")
    _INITIALIZED = True
    return _PHONEME_MODEL, _PHONEME_EXTRACTOR


def get_pipeline_status() -> dict:
    load_hubert_pipeline()
    return dict(_STATUS)


# --------------------------------------------------------------------------------------
# Decoding
# --------------------------------------------------------------------------------------
def _to_numpy(waveform: torch.Tensor) -> np.ndarray:
    if waveform.ndim > 1:
        waveform = waveform.squeeze()
    return waveform.detach().cpu().numpy().astype(np.float32)


CHUNK_SECONDS = 20  # long audio (paragraphs) is processed in pieces to keep memory low
FRAME_SEC = 0.02    # HuBERT emits one frame every 20 ms


def _chunks(samples: np.ndarray):
    """Yields (offset_seconds, piece)."""
    size = CHUNK_SECONDS * SAMPLE_RATE
    for start in range(0, len(samples), size):
        piece = samples[start:start + size]
        if len(piece) > SAMPLE_RATE * 0.1:      # skip tiny leftovers (<100 ms)
            yield start / SAMPLE_RATE, piece


def _decode_phoneme_model(samples: np.ndarray):
    all_ph, all_conf, all_ts = [], [], []
    for offset, piece in _chunks(samples):
        ph, conf, ts = _decode_phoneme_chunk(piece)
        all_ph.extend(ph)
        all_conf.extend(conf)
        all_ts.extend([[round(offset + a, 2), round(offset + b, 2)] for a, b in ts])
    return all_ph, all_conf, all_ts


def _decode_phoneme_chunk(samples: np.ndarray):
    inputs = _PHONEME_EXTRACTOR(samples, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    input_values = inputs.input_values.to(DEVICE)
    with torch.no_grad():
        logits = _PHONEME_MODEL(input_values)
        probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
    predictions = probs.argmax(axis=-1)

    # Collapse CTC frames into runs; drop 1-frame flickers and low-confidence runs
    # (these cause long garbage sequences and PER values far above 100%).
    decoded, confidences, times = [], [], []
    i, n = 0, len(predictions)
    while i < n:
        p = int(predictions[i])
        j = i
        while j < n and int(predictions[j]) == p:
            j += 1
        if p != _BLANK_IDX and p < len(_LABELS) and to_phoneme(_LABELS[p]) in PHONE_SET:
            run_conf = float(np.mean([probs[k][p] for k in range(i, j)]))
            if (j - i) >= MIN_RUN_FRAMES and run_conf >= MIN_RUN_CONF:
                decoded.append(to_phoneme(_LABELS[p]))
                confidences.append(run_conf)
                times.append((i * FRAME_SEC, j * FRAME_SEC))
        i = j
    return decoded, confidences, times


def _decode_asr(samples: np.ndarray):
    texts, confs = [], []
    for _, piece in _chunks(samples):
        inputs = _ASR_PROCESSOR(piece, sampling_rate=SAMPLE_RATE, return_tensors="pt")
        with torch.no_grad():
            logits = _ASR_MODEL(inputs.input_values.to(DEVICE)).logits
        probs = torch.softmax(logits, dim=-1)[0]
        ids = probs.argmax(dim=-1)
        texts.append(_ASR_PROCESSOR.batch_decode(ids.unsqueeze(0))[0].strip().lower())
        confs.append(float(probs.max(dim=-1).values.mean().item()))
    transcript = " ".join(t for t in texts if t)
    conf = float(np.mean(confs)) if confs else 0.0
    phones = word_to_phonemes(transcript) if transcript else []
    return phones, [conf] * len(phones), transcript


def _decode_demo(samples: np.ndarray, target_word: str):
    """Offline demo heuristic. NOT speech recognition - results are labelled as demo data."""
    expected = word_to_phonemes(target_word.strip()) if target_word.strip() else []
    if not expected:
        return ["AH"], [0.5]
    try:
        import librosa
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=samples, sr=SAMPLE_RATE)[0]))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=samples)[0]))
    except Exception:
        centroid, zcr = 2000.0, 0.05

    detected, conf = [], []
    for ph in expected:
        if ph == "R" and (centroid < 1800 or zcr < 0.03):
            detected.append("W")
        elif ph == "S" and centroid < 3500:
            detected.append("TH")
        elif ph == "K" and centroid > 3800:
            detected.append("T")
        else:
            detected.append(ph)
        conf.append(0.5)
    return detected, conf


def decode_with_mode(waveform: torch.Tensor, target_word: str = ""):
    """
    Returns a dict:
      phonemes, confidences, mode, transcript, warning
    """
    load_hubert_pipeline()
    samples = _to_numpy(waveform)
    mode = _STATUS["mode"]

    # Silence / empty audio -> nothing was said
    if samples.size == 0 or float(np.sqrt(np.mean(samples ** 2))) < 1e-4:
        return {"phonemes": [], "confidences": [], "mode": mode, "transcript": "",
                "warning": "No speech detected in the audio. Please record again closer to the microphone."}

    if mode == "hubert_phoneme":
        try:
            ph, conf, ts = _decode_phoneme_model(samples)
            return {"phonemes": ph, "confidences": conf, "mode": mode, "transcript": "", "warning": None,
                    "timestamps": ts}
        except Exception as exc:
            _log(f"Phoneme inference failed: {exc}")

    if mode in ("hubert_phoneme", "hubert_asr"):
        if _ASR_MODEL is None:
            _load_asr_model()
        if _ASR_MODEL is not None:
            try:
                ph, conf, text = _decode_asr(samples)
                return {"phonemes": ph, "confidences": conf, "mode": "hubert_asr", "transcript": text,
                        "warning": "Using speech-recognition mode (word level). "
                                   "Add the trained checkpoint to /models for exact phoneme detection."}
            except Exception as exc:
                _log(f"ASR inference failed: {exc}")

    if ALLOW_DEMO_FALLBACK:
        ph, conf = _decode_demo(samples, target_word)
        return {"phonemes": ph, "confidences": conf, "mode": "demo_fallback", "transcript": "",
                "warning": "DEMO MODE: no neural model is loaded, so these results are NOT based on "
                           "your real speech. Run models/download_model.py (internet needed) to enable "
                           "real analysis."}

    raise RuntimeError("No speech model could be loaded. Run backend/check_setup.py for details.")


def decode_speech_audio(waveform: torch.Tensor, target_word: str = "") -> tuple[list[str], list[float]]:
    """Backwards-compatible wrapper returning (phonemes, confidences)."""
    r = decode_with_mode(waveform, target_word)
    return r["phonemes"], r["confidences"]
