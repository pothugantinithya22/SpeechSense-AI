import re
import numpy as np
import pronouncing

# Standard CMU 39 Phonemes
CMU_PHONEMES = sorted([
    "AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER",
    "EY", "F", "G", "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG",
    "OW", "OY", "P", "R", "S", "SH", "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH"
])

PHONE_SET = set(CMU_PHONEMES)

def word_to_phonemes(text: str) -> list[str]:
    """
    Converts ANY word, name, sentence or paragraph to a CMU phoneme sequence.
    Dictionary words use CMUdict; unknown words/names use a G2P fallback.
    Numbers are spoken out. Lexical stress markers are removed.
    """
    from app.services.g2p import expand_numbers, fallback_g2p
    words = re.findall(r"[a-zA-Z']+", expand_numbers(text).lower())
    phonemes = []

    for raw_word in words:
        word = raw_word.strip("'")
        if not word:
            continue
        phones_list = pronouncing.phones_for_word(word)
        if phones_list:
            phones = [re.sub(r"\d+", "", p).upper() for p in phones_list[0].split()]
            cleaned = [p for p in phones if p in PHONE_SET]
        else:
            cleaned = [p for p in fallback_g2p(word) if p in PHONE_SET]
        phonemes.extend(cleaned)

    return phonemes

def align_phonemes(expected: list[str], detected: list[str]) -> tuple[list[str], list[str], int, int, int]:
    """
    Computes optimal Levenshtein alignment between expected and detected phoneme sequences.
    Returns:
      (aligned_expected, aligned_detected, substitutions, omissions, insertions)
    """
    rows = len(expected)
    cols = len(detected)
    matrix = np.zeros((rows + 1, cols + 1), dtype=int)

    for r in range(rows + 1):
        matrix[r][0] = r
    for c in range(cols + 1):
        matrix[0][c] = c

    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            cost = 0 if expected[r - 1] == detected[c - 1] else 1
            matrix[r][c] = min(
                matrix[r - 1][c] + 1,       # deletion / omission
                matrix[r][c - 1] + 1,       # insertion
                matrix[r - 1][c - 1] + cost # match or substitution
            )

    # Backtracking
    aligned_exp = []
    aligned_det = []
    r, c = rows, cols

    while r > 0 or c > 0:
        if r > 0 and c > 0 and matrix[r][c] == matrix[r - 1][c - 1] + (0 if expected[r - 1] == detected[c - 1] else 1):
            aligned_exp.append(expected[r - 1])
            aligned_det.append(detected[c - 1])
            r -= 1
            c -= 1
        elif r > 0 and matrix[r][c] == matrix[r - 1][c] + 1:
            aligned_exp.append(expected[r - 1])
            aligned_det.append("-")
            r -= 1
        else:
            aligned_exp.append("-")
            aligned_det.append(detected[c - 1])
            c -= 1

    aligned_exp.reverse()
    aligned_det.reverse()

    subs = 0
    omiss = 0
    ins = 0

    for exp_p, det_p in zip(aligned_exp, aligned_det):
        if exp_p == "-":
            ins += 1
        elif det_p == "-":
            omiss += 1
        elif exp_p != det_p:
            subs += 1

    return aligned_exp, aligned_det, subs, omiss, ins

def calculate_metrics(expected: list[str], detected: list[str]) -> dict:
    """
    Computes overall accuracy %, PER %, and detailed alignment list.
    """
    if not expected:
        return {
            "accuracy": 0.0,
            "per": 0.0,
            "alignment": [],
            "error_count": len(detected)
        }

    aligned_exp, aligned_det, subs, omiss, ins = align_phonemes(expected, detected)
    total_expected = len(expected)
    edit_dist = subs + omiss + ins

    # Phoneme Error Rate (PER)
    per = round((edit_dist / max(total_expected, 1)) * 100.0, 2)

    # Correct matching count
    correct_count = sum(1 for e, d in zip(aligned_exp, aligned_det) if e == d and e != "-")
    accuracy = round((correct_count / max(total_expected, 1)) * 100.0, 2)

    alignment_items = []
    for exp_p, det_p in zip(aligned_exp, aligned_det):
        if exp_p == det_p:
            st = "correct"
        elif exp_p == "-":
            st = "insertion"
        elif det_p == "-":
            st = "omission"
        else:
            st = "substitution"

        alignment_items.append({
            "expected": f"/{exp_p}/" if exp_p != "-" else "-",
            "detected": f"/{det_p}/" if det_p != "-" else "-",
            "status": st,
            "raw_expected": exp_p,
            "raw_detected": det_p
        })

    return {
        "accuracy": accuracy,
        "per": per,
        "alignment": alignment_items,
        "substitutions": subs,
        "omissions": omiss,
        "insertions": ins,
        "error_count": subs + omiss + ins
    }
