"""Run this FIRST:  cd backend && python check_setup.py
Tells you exactly which speech mode SpeechSense will use and why."""
import sys, importlib

print("Python", sys.version.split()[0])
missing = []
for mod in ["fastapi", "uvicorn", "torch", "torchaudio", "transformers", "librosa",
            "soundfile", "pronouncing", "huggingface_hub", "multipart", "dotenv"]:
    try:
        importlib.import_module(mod)
        print(f"  OK       {mod}")
    except Exception as e:
        print(f"  MISSING  {mod}  ({e})")
        missing.append(mod)
if missing:
    print("\nInstall the missing packages with:  pip install -r requirements.txt")
    sys.exit(1)

from app.config import HF_MODEL_PATH, HF_HUBERT_MODEL
from app.models.hubert_pipeline import get_pipeline_status
print("\nExpected checkpoint path:", HF_MODEL_PATH)
status = get_pipeline_status()
print("\nACTIVE MODE:", status["mode"])
for m in status["messages"]:
    print("  -", m)
if status["mode"] == "hubert_phoneme":
    print("\nPerfect - the trained phoneme model is analysing your real audio.")
elif status["mode"] == "hubert_asr":
    print("\nWorking (word-level). For exact phoneme detection put best_cmu_93.2pct.pt in the models/ folder.")
else:
    print("\nDEMO MODE: no real analysis. Connect to the internet once and run:\n  python ../models/download_model.py")

if any("label order is unknown" in m for m in status["messages"]):
    print("\n>>> The checkpoint's label order is unknown. Run:  python inspect_checkpoint.py   and send me its output.")
