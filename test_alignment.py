import os
import sys
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.alignment import word_to_phonemes, align_phonemes, calculate_metrics

def test_word_to_phonemes():
    phones = word_to_phonemes("rabbit")
    assert "R" in phones
    assert len(phones) >= 4

    phones_sun = word_to_phonemes("sun")
    assert phones_sun == ["S", "AH", "N"]

def test_align_phonemes_perfect_match():
    expected = ["R", "AE", "B", "AH", "T"]
    detected = ["R", "AE", "B", "AH", "T"]
    aligned_exp, aligned_det, subs, omiss, ins = align_phonemes(expected, detected)
    assert subs == 0
    assert omiss == 0
    assert ins == 0
    assert aligned_exp == aligned_det

def test_align_phonemes_substitution():
    expected = ["R", "AE", "B", "AH", "T"]
    detected = ["W", "AE", "B", "AH", "T"]
    aligned_exp, aligned_det, subs, omiss, ins = align_phonemes(expected, detected)
    assert subs == 1
    assert omiss == 0
    assert ins == 0

def test_align_phonemes_omission():
    expected = ["S", "T", "AA", "R"]
    detected = ["T", "AA", "R"]
    aligned_exp, aligned_det, subs, omiss, ins = align_phonemes(expected, detected)
    assert omiss == 1

def test_calculate_metrics():
    expected = ["R", "AE", "B", "AH", "T"]
    detected = ["W", "AE", "B", "AH", "T"]
    metrics = calculate_metrics(expected, detected)
    assert metrics["accuracy"] == 80.0
    assert metrics["per"] == 20.0
    assert metrics["substitutions"] == 1
    assert len(metrics["alignment"]) == 5
