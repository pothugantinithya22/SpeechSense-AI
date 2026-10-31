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

def test_health_endpoint():
    response = client.get("/api/speech/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_visual_guidance_endpoint():
    response = client.get("/api/visual/phoneme/R")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "/r/"
    assert "svg_params" in data

def test_visual_all_endpoint():
    response = client.get("/api/visual/all")
    assert response.status_code == 200
    assert len(response.json()) >= 35

def test_progress_endpoint():
    response = client.get("/api/progress/1")
    assert response.status_code == 200
    data = response.json()
    assert data["child_name"] == "Leo Miller"
    assert "phoneme_mastery" in data
    assert "stars" in data

def test_therapist_patients_endpoint():
    response = client.get("/api/therapist/patients")
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) >= 2
    assert any(p["name"] == "Leo Miller" for p in patients)

def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "How do I help with the /r/ sound?"})
    assert response.status_code == 200
    assert "/r/" in response.json()["response"]
