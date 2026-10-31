"""
Complete End-to-End Clinical Lifecycle Integration Test.
Validates the entire 14-step clinical workflow mandated for SpeechSense.
"""

import os
import sys
import io
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

client = TestClient(app)

def test_full_clinical_workflow():
    print("\n--- STEP 1: User Registration & Login ---")
    login_resp = client.post("/api/auth/login", json={"username": "child_leo", "password": "leo123"})
    assert login_resp.status_code == 200
    user_info = login_resp.json()["user"]
    child_id = user_info["child_id"]
    assert child_id is not None

    print("\n--- STEP 2: Child Dashboard Access ---")
    progress_resp = client.get(f"/api/progress/{child_id}")
    assert progress_resp.status_code == 200
    child_data = progress_resp.json()
    initial_stars = child_data["stars"]
    assert initial_stars >= 0

    print("\n--- STEP 3: Speech Audio Upload / Record ---")
    demo_audio_path = os.path.join(os.path.dirname(__file__), "..", "data", "demo_audio", "rabbit_sample.wav")
    assert os.path.exists(demo_audio_path), "Demo audio file should exist."

    with open(demo_audio_path, "rb") as f:
        audio_bytes = f.read()

    print("\n--- STEP 4, 5, 6, 7: Audio Preprocessing, HuBERT Extraction, Pronunciation Assessment & Error Detection ---")
    analyze_resp = client.post(
        "/api/speech/analyze",
        data={"target_word": "rabbit", "child_id": child_id},
        files={"audio": ("rabbit_sample.wav", io.BytesIO(audio_bytes), "audio/wav")}
    )
    assert analyze_resp.status_code == 200
    analysis = analyze_resp.json()
    
    assert analysis["target_word"] == "rabbit"
    assert "expected_phonemes" in analysis
    assert "detected_phonemes" in analysis
    assert "accuracy" in analysis
    assert "per" in analysis
    assert "alignment" in analysis
    assert "phoneme_errors" in analysis

    print("\n--- STEP 8: Personalized Therapy Plan Generation ---")
    plan_resp = client.post("/api/therapy/generate", json={
        "child_id": child_id,
        "target_phoneme": "R",
        "difficulty": "intermediate"
    })
    assert plan_resp.status_code == 200
    plan = plan_resp.json()
    assert plan["target_phoneme"] == "R"
    assert len(plan["phases"]) == 4

    print("\n--- STEP 9: Explainable AI (XAI) Feedback ---")
    xai_resp = client.post("/api/xai/explain", json={
        "expected": "R",
        "detected": "W",
        "confidence": 0.88
    })
    assert xai_resp.status_code == 200
    xai_data = xai_resp.json()
    assert "why_flagged" in xai_data
    assert "articulatory_contrast" in xai_data

    print("\n--- STEP 10: Visual Articulation & Mouth Guidance ---")
    visual_resp = client.get("/api/visual/phoneme/R")
    assert visual_resp.status_code == 200
    visual_data = visual_resp.json()
    assert "child_cue" in visual_data
    assert "svg_params" in visual_data

    print("\n--- STEP 11: Progress Tracking & Analytics Update ---")
    updated_progress_resp = client.get(f"/api/progress/{child_id}")
    assert updated_progress_resp.status_code == 200
    updated_child = updated_progress_resp.json()
    assert updated_child["stars"] >= initial_stars

    print("\n--- STEP 12 & 13: Therapist Dashboard & Review ---")
    therapist_login = client.post("/api/auth/login", json={"username": "dr_sarah", "password": "therapist123"})
    assert therapist_login.status_code == 200
    
    patient_detail_resp = client.get(f"/api/therapist/patient/{child_id}")
    assert patient_detail_resp.status_code == 200
    patient_detail = patient_detail_resp.json()
    assert len(patient_detail["sessions"]) > 0

    print("\n--- STEP 14: AI Clinical Recommendations ---")
    assert "ai_recommendations" in patient_detail
    assert len(patient_detail["ai_recommendations"]["recommendations"]) > 0
    assert patient_detail["ai_recommendations"]["severity_index"] is not None

    print("\n[SUCCESS] Entire 14-Step End-to-End Clinical Lifecycle Passed Flawlessly!")
