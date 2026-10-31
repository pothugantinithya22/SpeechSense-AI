import os
import sys
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.therapy_generator import generate_therapy_plan

def test_generate_therapy_plan_r():
    plan = generate_therapy_plan("R", child_id=1, difficulty="intermediate")
    assert plan["target_phoneme"] == "R"
    assert "Rhotic" in plan["title"]
    assert len(plan["phases"]) == 4
    # Phase 1 isolation
    assert plan["phases"][0]["phase"] == 1
    assert "Isolation" in plan["phases"][0]["name"]
    # Phase 2 syllables
    assert plan["phases"][1]["phase"] == 2
    # Phase 3 words
    assert plan["phases"][2]["phase"] == 3
    # Phase 4 sentences
    assert plan["phases"][3]["phase"] == 4

def test_generate_therapy_plan_s():
    plan = generate_therapy_plan("S", child_id=2)
    assert plan["target_phoneme"] == "S"
    assert "Sibilant" in plan["title"]
    assert len(plan["phases"]) == 4
