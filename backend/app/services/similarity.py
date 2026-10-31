"""Similarity scoring: how close is the produced sound to the expected one (articulatory features)."""
from app.services.visual_mouth_data import PHONEME_ARTICULATION_DATA

# vowel features: (height 0-3, backness 0-1, rounded 0/1)
_VOWELS = {"IY": (3, 0, 0), "IH": (2.5, .5, 0), "EY": (2, 0, 0), "EH": (1.5, .3, 0), "AE": (1, .2, 0),
           "AA": (0, 1, 0), "AO": (1, 1, 1), "OW": (2, 1, 1), "UH": (2.5, .9, 1), "UW": (3, 1, 1),
           "AH": (1.5, .7, 0), "ER": (1.5, .6, 0), "AW": (.5, .8, 1), "AY": (.5, .5, 0), "OY": (1.5, 1, 1)}


def _cons_features(p):
    d = PHONEME_ARTICULATION_DATA.get(p)
    if not d:
        return None
    return (d["manner"].split("(")[0].strip().lower(), d["place"].lower(), d["voicing"].lower())


def phoneme_similarity(a: str, b: str) -> float:
    """0.0 - 1.0"""
    if a == b:
        return 1.0
    if a in _VOWELS and b in _VOWELS:
        va, vb = _VOWELS[a], _VOWELS[b]
        dist = abs(va[0] - vb[0]) / 3 * 0.4 + abs(va[1] - vb[1]) * 0.4 + abs(va[2] - vb[2]) * 0.2
        return round(max(0.0, 1 - dist), 2)
    if a in _VOWELS or b in _VOWELS:
        return 0.0
    fa, fb = _cons_features(a), _cons_features(b)
    if not fa or not fb:
        return 0.0
    return round(0.4 * (fa[0] == fb[0]) + 0.4 * (fa[1] == fb[1]) + 0.2 * (fa[2] == fb[2]), 2)


def similarity_score(alignment: list[dict]) -> float:
    """Overall pronunciation similarity, 0-100 (omissions and extra sounds score 0)."""
    if not alignment:
        return 0.0
    total = 0.0
    for it in alignment:
        e, d = it["raw_expected"], it["raw_detected"]
        if it["status"] == "correct":
            total += 1.0
        elif it["status"] == "substitution":
            total += phoneme_similarity(e, d)
    return round(total / len(alignment) * 100, 1)
