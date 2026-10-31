# SpeechSense - how to run (fixed version)

## 1. Backend (Python 3.10 - 3.12)
```
cd backend
python -m venv venv
venv\Scripts\activate          (Windows)      source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
python ../models/download_model.py     # ONE TIME, needs internet (downloads the trained checkpoint)
python check_setup.py                  # must print  ACTIVE MODE: hubert_phoneme  (or hubert_asr)
uvicorn app.main:app --reload --port 8000
```
On first start the backend also downloads `facebook/hubert-large-ls960-ft` (~1.2 GB) automatically.

## 2. Frontend (Node 18+)
```
cd frontend
npm install
npm start
```
Open http://localhost:3000  (login demo: child_leo / leo123, therapist: dr_sarah / therapist123)

## 3. Test with REAL speech
Record with the microphone in the Analyze page, or run `python data/generate_real_demo_audio.py`.
The old demo .wav files are sine tones, not voices - they can never give correct phonemes.

## What the result banner means
- no banner + mode hubert_phoneme -> real phoneme analysis (best)
- yellow "speech-recognition mode"  -> works, word level
- yellow "DEMO MODE"               -> NOT real analysis; models are not downloaded yet

## Works for ANY text
Type any word, name, sentence or paragraph as the target (the box is multi-line) and say exactly that.
Dictionary words use CMUdict; names/unknown words use a built-in letter-to-sound fallback (approximate).
Audio up to 120 s is supported (set MAX_AUDIO_DURATION_SEC in backend/.env to change it).

## Pipeline (matches the project review slides)
Speech input -> Data preprocessing (resample, noise reduction, cleaning, segmentation) -> HuBERT feature extraction -> Pronunciation assessment (phoneme classification, mispronunciation detection, similarity scoring, error localization with timestamps) -> Explainable AI + mouth guidance -> Personalized therapy plan (weak sounds, difficulty, exercises) -> Therapist dashboard. The Analyze page shows each stage after every attempt.
ALWAYS make the target text match what you actually say, otherwise errors/PER will be high.
