from app.services.g2p import rule_g2p, number_to_words
from app.services.alignment import word_to_phonemes, PHONE_SET


def test_rule_g2p_names_and_unknown_words():
    for w in ["saiteja", "hyderabad", "zorblax", "knife", "school"]:
        ph = rule_g2p(w)
        assert ph and all(p in PHONE_SET for p in ph)


def test_numbers_spoken():
    assert number_to_words(42) == "forty two"


def test_paragraph_has_phonemes_for_every_word():
    text = "Hello my name is Saiteja. I live in Hyderabad and I am 21 years old."
    assert len(word_to_phonemes(text)) > 30


def test_similarity_and_signal_ops():
    import numpy as np
    from app.services.similarity import phoneme_similarity, similarity_score
    from app.services.signal_ops import reduce_noise, segment_speech
    assert phoneme_similarity("R", "R") == 1.0
    assert 0.0 < phoneme_similarity("S", "TH") < 1.0
    sr = 16000
    t = np.arange(sr * 2) / sr
    sig = (np.where((t > 0.4) & (t < 1.5), 0.5 * np.sin(2 * np.pi * 220 * t), 0)
           + 0.03 * np.random.randn(len(t))).astype(np.float32)
    clean = reduce_noise(sig, sr)
    assert len(clean) == len(sig)
    assert np.std(clean[: int(0.3 * sr)]) < np.std(sig[: int(0.3 * sr)])
    assert len(segment_speech(clean, sr)) >= 1
    al = [{"raw_expected": "R", "raw_detected": "R", "status": "correct"}]
    assert similarity_score(al) == 100.0


def test_label_extraction():
    from app.services.label_utils import extract_labels, to_phoneme
    labels, blank, _ = extract_labels({"phonemes": ["AA", "AE", "B", "<blank>"]}, 4)
    assert blank == 3 and labels[0] == "AA"
    assert extract_labels({}, 38)[0] is None
    assert to_phoneme("<blank>") is None and to_phoneme("AH0") == "AH"
