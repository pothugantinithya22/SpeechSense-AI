"""Finds out which phoneme each output class of a trained checkpoint stands for.
Pure Python (no torch) so it can be tested anywhere."""
import json
import re
from pathlib import Path

BLANK_NAMES = {"<blank>", "blank", "<pad>", "[pad]", "pad", "_", "-", "|", "<ctc>", "[blank]", "<unk>", "[unk]", "<eps>"}
SKIP_NAMES = {"sil", "sp", "spn", "<sil>", "<space>", "<s>", "</s>", " "}
LABEL_KEYS = ["phonemes", "phoneme_list", "phone_list", "labels", "vocab", "classes", "idx_to_phone",
              "id2label", "index_to_phone", "idx2phone", "phone2idx", "phone_to_idx", "phone_to_id",
              "label2id", "phoneme_to_idx", "phoneme2idx", "vocab_dict", "idx_to_phoneme", "itos", "stoi"]


def _normalize(label: str) -> str:
    return re.sub(r"\d+", "", str(label)).strip().upper()


def _as_list(obj, n_classes):
    """list -> list; dict (either direction) -> list ordered by index."""
    if isinstance(obj, (list, tuple)) and all(isinstance(x, str) for x in obj):
        return list(obj)
    if isinstance(obj, dict) and obj:
        items = list(obj.items())
        if all(isinstance(k, str) and isinstance(v, int) for k, v in items):       # label -> idx
            items = [(v, k) for k, v in items]
        if all(isinstance(k, (int, str)) and str(k).lstrip("-").isdigit() and isinstance(v, str) for k, v in items):
            by_idx = {int(k): v for k, v in items}
            if by_idx and max(by_idx) < n_classes + 5:
                return [by_idx.get(i, "?") for i in range(max(by_idx) + 1)]
    return None


def extract_labels(checkpoint, n_classes: int, labels_file: Path | None = None):
    """Returns (labels, blank_index, source) or (None, None, reason)."""
    candidates = []
    if labels_file and Path(labels_file).is_file():
        try:
            data = json.loads(Path(labels_file).read_text(encoding="utf-8"))
            if isinstance(data, dict) and "labels" in data:
                lst = _as_list(data["labels"], n_classes)
                if lst:
                    blank = data.get("blank_index")
                    candidates.append((lst, blank, f"models/{Path(labels_file).name}"))
            else:
                lst = _as_list(data, n_classes)
                if lst:
                    candidates.append((lst, None, f"models/{Path(labels_file).name}"))
        except Exception:
            pass
    if isinstance(checkpoint, dict):
        holders = [checkpoint] + [v for v in checkpoint.values() if isinstance(v, dict) and len(v) < 200]
        for holder in holders:
            for key in LABEL_KEYS:
                if key in holder:
                    lst = _as_list(holder[key], n_classes)
                    if lst:
                        candidates.append((lst, None, f"checkpoint['{key}']"))
    for lst, blank, src in candidates:
        if len(lst) == n_classes:
            if blank is None:
                blank = next((i for i, l in enumerate(lst) if str(l).strip().lower() in BLANK_NAMES), None)
            if blank is None:
                blank = n_classes - 1       # CTC blank is conventionally the last class in this project
                src += " (blank assumed last)"
            return lst, blank, src
        if len(lst) == n_classes - 1:       # blank not listed
            return list(lst) + ["<blank>"], n_classes - 1, src + " (+blank appended last)"
    return None, None, "no label list found in the checkpoint or models/phoneme_labels.json"


def to_phoneme(label: str):
    """Normalised CMU phoneme, or None if the label should be ignored (blank, silence ...)."""
    low = str(label).strip().lower()
    if low in BLANK_NAMES or low in SKIP_NAMES:
        return None
    return _normalize(label)
