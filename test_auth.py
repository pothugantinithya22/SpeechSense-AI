import os
import sys
import pytest

# Ensure backend package is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, hash_password

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

client = TestClient(app)

def test_demo_users_endpoint():
    response = client.get("/api/auth/demo-users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = [u["username"] for u in data]
    assert "child_leo" in usernames
    assert "dr_sarah" in usernames

def test_login_success_child():
    response = client.post("/api/auth/login", json={"username": "child_leo", "password": "leo123"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["role"] == "child"
    assert data["user"]["full_name"] == "Leo Miller"
    assert data["user"]["child_id"] is not None

def test_login_success_therapist():
    response = client.post("/api/auth/login", json={"username": "dr_sarah", "password": "therapist123"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "therapist"
    assert "Dr. Sarah" in data["user"]["full_name"]

def test_login_invalid_password():
    response = client.post("/api/auth/login", json={"username": "child_leo", "password": "wrongpassword"})
    assert response.status_code == 401

def test_register_new_child():
    import uuid
    unique_user = f"child_test_{uuid.uuid4().hex[:6]}"
    response = client.post("/api/auth/register", json={
        "username": unique_user,
        "password": "testpass123",
        "full_name": "Test Child",
        "role": "child",
        "age": 8,
        "diagnosis": "Mild lisp"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == unique_user
    assert data["user"]["child_id"] is not None
