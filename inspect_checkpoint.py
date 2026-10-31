"""Run:  python inspect_checkpoint.py
Shows what the trained checkpoint contains, so we can find out which sound each output class means."""
import sys
from pathlib import Path
import torch
from app.config import HF_MODEL_PATH, HF_MODEL_REPO
from app.services.label_utils import extract_labels

path = HF_MODEL_PATH
print("Checkpoint:", path)
ck = torch.load(path, map_location="cpu", weights_only=False)
print("Type:", type(ck).__name__)

if isinstance(ck, dict):
    print("\nTop-level keys:")
    for k, v in ck.items():
        if isinstance(v, torch.Tensor):
            desc = f"tensor {tuple(v.shape)}"
        elif isinstance(v, dict):
            desc = f"dict with {len(v)} entries"
        elif isinstance(v, (list, tuple)):
            desc = f"{type(v).__name__} of {len(v)}: {list(v)[:45]}"
        else:
            desc = f"{type(v).__name__}: {str(v)[:80]}"
        print(f"  {k}: {desc}")
    sd = ck.get("model") or ck.get("model_state_dict") or ck.get("state_dict") or ck
    outs = [(k, v.shape) for k, v in sd.items() if k.startswith("projection.") and k.endswith("weight")]
    print("\nProjection layers:", outs)
    n = outs[-1][1][0] if outs else 38
    labels, blank, src = extract_labels(ck, n, Path(path).parent / "phoneme_labels.json")
    print("\nLabel search:", src)
    if labels:
        print("Blank index:", blank)
        for i, l in enumerate(labels):
            print(f"  {i:2d} -> {l}")

try:
    from huggingface_hub import list_repo_files
    print("\nFiles in", HF_MODEL_REPO, ":")
    for f in list_repo_files(HF_MODEL_REPO):
        print("  ", f)
except Exception as e:
    print("\n(could not list repo files:", e, ")")
