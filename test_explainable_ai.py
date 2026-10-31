import os
import sys
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.explainable_ai import generate_xai_explanation

def test_xai_gliding_explanation():
    diag = generate_xai_explanation("R", "W", confidence=0.89)
    assert diag["expected_phoneme"] == "/R/"
    assert diag["detected_phoneme"] == "/W/"
    assert "Gliding" in diag["error_classification"]
    assert "F3" in diag["why_flagged"]
    assert "articulatory_contrast" in diag
    assert "tongue_guidance" in diag["articulatory_contrast"]
    assert diag["confidence_score"] == 89.0

def test_xai_lisp_explanation():
    diag = generate_xai_explanation("S", "TH", confidence=0.91)
    assert "Lisp" in diag["error_classification"]
    assert diag["articulatory_contrast"]["expected_place"] == "Alveolar Ridge"
    assert "Interdental" in diag["articulatory_contrast"]["detected_place"]

def test_xai_omission():
    diag = generate_xai_explanation("R", "-", confidence=0.75)
    assert "Omission" in diag["error_classification"]
    assert "omitted" in diag["detected_phoneme"]
