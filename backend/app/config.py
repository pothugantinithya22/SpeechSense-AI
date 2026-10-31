import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent          # .../backend
PROJECT_DIR = BASE_DIR.parent                               # .../SpeechSense
load_dotenv(BASE_DIR / ".env")

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ENV = os.getenv("ENV", "development")

# Database
DB_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "speechsense.db"))

# Models
HF_MODEL_REPO = os.getenv("HF_MODEL_REPO", "akshithawork1422/neurospace")
HF_MODEL_FILE = os.getenv("HF_MODEL_FILE", "best_cmu_93.2pct.pt")
HF_HUBERT_MODEL = os.getenv("HF_HUBERT_MODEL", "facebook/hubert-large-ls960-ft")
DEVICE = os.getenv("DEVICE", "cpu")

# Folder that holds the trained checkpoint (SpeechSense/models). Always an absolute path,
# so it no longer depends on the directory you start uvicorn from.
MODEL_DIR = Path(os.getenv("MODEL_DIR", str(PROJECT_DIR / "models")))
HF_MODEL_PATH = str(MODEL_DIR / HF_MODEL_FILE)

# 1 = download missing models from Hugging Face automatically (needs internet, first run only)
ENABLE_HF_DOWNLOAD = os.getenv("ENABLE_HF_DOWNLOAD", "1") == "1"
# 1 = force fully offline mode (never contact Hugging Face)
OFFLINE = os.getenv("SPEECHSENSE_OFFLINE", "0") == "1"
# 1 = if no neural model can be loaded, use the clearly-labelled demo heuristic instead of failing
ALLOW_DEMO_FALLBACK = os.getenv("ALLOW_DEMO_FALLBACK", "1") == "1"

# Audio processing
SAMPLE_RATE = 16000
MAX_AUDIO_DURATION_SEC = float(os.getenv("MAX_AUDIO_DURATION_SEC", 120))  # long paragraphs supported

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
