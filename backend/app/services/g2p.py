"""
Grapheme-to-phoneme fallback so SpeechSense works for ANY word, name or paragraph.

Order used for each word:
  1. CMU dictionary (via `pronouncing`)      - exact, ~134k English words
  2. g2p_en neural model, if installed       - good for unseen words
  3. built-in rule-based converter (below)   - always available, approximate
Numbers are spoken out ("42" -> "forty two") before conversion.
"""
import re

VOWELS = set("aeiou")

# ---------- numbers -> words ----------
_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def number_to_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + number_to_words(n % 100))
    if n < 1_000_000:
        return number_to_words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + number_to_words(n % 1000))
    return " ".join(_ONES[int(d)] for d in str(n))  # very large: read digit by digit


def expand_numbers(text: str) -> str:
    return re.sub(r"\d+", lambda m: " " + number_to_words(int(m.group())) + " ", text)


# ---------- rule based letter-to-sound ----------
# (pattern, phonemes, only_at_start, only_at_end)
_PATTERNS = [
    ("tch", ["CH"], 0, 0), ("dge", ["JH"], 0, 0), ("igh", ["AY"], 0, 0),
    ("tion", ["SH", "AH", "N"], 0, 0), ("sion", ["ZH", "AH", "N"], 0, 0),
    ("sch", ["S", "K"], 0, 0), ("ough", ["AO"], 0, 0),
    ("kn", ["N"], 1, 0), ("wr", ["R"], 1, 0), ("gn", ["N"], 1, 0), ("ps", ["S"], 1, 0),
    ("mb", ["M"], 0, 1),
    ("sh", ["SH"], 0, 0), ("ch", ["CH"], 0, 0), ("th", ["TH"], 0, 0), ("ph", ["F"], 0, 0),
    ("wh", ["W"], 0, 0), ("ck", ["K"], 0, 0), ("ng", ["NG"], 0, 0), ("nk", ["NG", "K"], 0, 0),
    ("qu", ["K", "W"], 0, 0), ("gh", [], 0, 0),
    ("ee", ["IY"], 0, 0), ("ea", ["IY"], 0, 0), ("oo", ["UW"], 0, 0), ("ai", ["EY"], 0, 0),
    ("ay", ["EY"], 0, 0), ("oa", ["OW"], 0, 0), ("ou", ["AW"], 0, 0), ("oi", ["OY"], 0, 0),
    ("oy", ["OY"], 0, 0), ("au", ["AO"], 0, 0), ("aw", ["AO"], 0, 0), ("ie", ["IY"], 0, 0),
    ("ei", ["EY"], 0, 0), ("ew", ["UW"], 0, 0), ("ue", ["UW"], 0, 0),
    ("ow", ["OW"], 0, 1), ("ow", ["AW"], 0, 0),
    ("ar", ["AA", "R"], 0, 0), ("or", ["AO", "R"], 0, 0),
    ("er", ["ER"], 0, 0), ("ir", ["ER"], 0, 0), ("ur", ["ER"], 0, 0),
]
_SINGLE_CONS = {"b": "B", "d": "D", "f": "F", "h": "HH", "j": "JH", "k": "K", "l": "L", "m": "M",
                "n": "N", "p": "P", "q": "K", "r": "R", "t": "T", "v": "V", "w": "W", "z": "Z"}
_SHORT = {"a": "AE", "e": "EH", "i": "IH", "o": "AA", "u": "AH"}
_LONG = {"a": "EY", "e": "IY", "i": "AY", "o": "OW", "u": "UW"}
_VOICED_END = set("aeiouybdglmnrv")


def rule_g2p(word: str) -> list[str]:
    w = re.sub(r"[^a-z]", "", word.lower())
    n = len(w)
    out: list[str] = []
    i = 0
    while i < n:
        rest = w[i:]
        matched = False
        for pat, ph, at_start, at_end in _PATTERNS:
            if not rest.startswith(pat):
                continue
            if at_start and i != 0:
                continue
            if at_end and i + len(pat) != n:
                continue
            out.extend(ph)
            i += len(pat)
            matched = True
            break
        if matched:
            continue

        c = w[i]
        nxt = w[i + 1] if i + 1 < n else ""
        if c in VOWELS:
            # silent final e (make -> M EY K)
            if c == "e" and i == n - 1 and n > 2 and w[i - 1] not in VOWELS:
                i += 1
                continue
            # magic-e: vowel + consonant + final 'e'  ->  long vowel
            if i + 2 == n - 1 and w[i + 2] == "e" and nxt and nxt not in VOWELS:
                out.append(_LONG[c])
            elif i == n - 1:  # word-final vowel
                out.append({"a": "AH", "e": "IY", "i": "IY", "o": "OW", "u": "UW"}[c])
            else:
                out.append(_SHORT[c])
        elif c == "y":
            if i == 0:
                out.append("Y")
            elif i == n - 1:
                vowel_groups = len(re.findall(r"[aeiou]+", w[:i]))
                out.append("IY" if vowel_groups >= 1 else "AY")
            else:
                out.append("IH")
        elif c == "c":
            out.append("S" if nxt in ("e", "i", "y") else "K")
        elif c == "g":
            out.append("JH" if nxt in ("e", "i", "y") else "G")
        elif c == "s":
            out.append("Z" if (i == n - 1 and i > 0 and w[i - 1] in _VOICED_END) else "S")
        elif c == "x":
            out.extend(["K", "S"])
        elif c in _SINGLE_CONS:
            if not (i > 0 and w[i - 1] == c):       # collapse double letters (rabbit -> rabit)
                out.append(_SINGLE_CONS[c])
        i += 1
    return out


_G2P_EN = None
_G2P_EN_TRIED = False


def _neural_g2p(word: str):
    """Optional: uses g2p_en if it is installed AND its data is available. Never raises."""
    global _G2P_EN, _G2P_EN_TRIED
    if not _G2P_EN_TRIED:
        _G2P_EN_TRIED = True
        try:
            from g2p_en import G2p
            _G2P_EN = G2p()
        except Exception:
            _G2P_EN = None
    if _G2P_EN is None:
        return None
    try:
        phones = [re.sub(r"\d+", "", p) for p in _G2P_EN(word) if re.match(r"^[A-Z]+\d?$", p)]
        return phones or None
    except Exception:
        return None


def fallback_g2p(word: str) -> list[str]:
    return _neural_g2p(word) or rule_g2p(word)
