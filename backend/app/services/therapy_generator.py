"""
Personalized Therapy Curriculum Generator for SpeechSense.
Generates structured multi-phase speech therapy protocols tailored to a child's
specific phoneme substitutions, omissions, and motor speech deficits.
"""

from app.services.visual_mouth_data import get_phoneme_articulation

# Comprehensive phoneme therapy database
THERAPY_CURRICULA = {
    "R": {
        "title": "Rhotic /r/ Precision Mastery",
        "description": "Progressive protocol addressing /r/ gliding substitutions through bunched/retroflex tongue conditioning.",
        "difficulty": "intermediate",
        "phases": [
            {
                "phase": 1,
                "name": "Phase 1: Sound in Isolation",
                "target": "/r/",
                "goal": "Elicit clean /r/ sound 10 consecutive times without lip rounding.",
                "status": "in_progress",
                "exercises": [
                    {"type": "cue", "instruction": "Make the 'growling bear' sound: /rrr/!", "target": "R", "repetitions": 10},
                    {"type": "mouth_guidance", "instruction": "Anchor sides of tongue to back top teeth. Keep lips smiling.", "target": "R"},
                    {"type": "listen_repeat", "prompt": "Listen to the model sound and repeat 5 times.", "target": "R", "repetitions": 5}
                ]
            },
            {
                "phase": 2,
                "name": "Phase 2: Syllable Combinations",
                "target": "/r/ + Vowels",
                "goal": "Seamlessly transition from /r/ into varied vowel nuclei.",
                "status": "locked",
                "exercises": [
                    {"type": "drill", "prompt": "Ray", "target": "R EY", "repetitions": 5},
                    {"type": "drill", "prompt": "Ree", "target": "R IY", "repetitions": 5},
                    {"type": "drill", "prompt": "Row", "target": "R OW", "repetitions": 5},
                    {"type": "drill", "prompt": "Rah", "target": "R AA", "repetitions": 5}
                ]
            },
            {
                "phase": 3,
                "name": "Phase 3: Word-Level Production",
                "target": "Initial & Medial /r/ Words",
                "goal": "Achieve 85% accuracy on target vocabulary words.",
                "status": "locked",
                "exercises": [
                    {"type": "word", "prompt": "Rabbit", "target": "R AE B AH T", "repetitions": 5},
                    {"type": "word", "prompt": "Rocket", "target": "R AA K AH T", "repetitions": 5},
                    {"type": "word", "prompt": "Rainbow", "target": "R EY N B OW", "repetitions": 5},
                    {"type": "word", "prompt": "Star", "target": "S T AA R", "repetitions": 5}
                ]
            },
            {
                "phase": 4,
                "name": "Phase 4: Sentence Fluency & Twisters",
                "target": "Conversational Fluency",
                "goal": "Maintain accurate /r/ articulation in continuous speech.",
                "status": "locked",
                "exercises": [
                    {"type": "sentence", "prompt": "The red rabbit ran quickly down the road.", "repetitions": 3},
                    {"type": "sentence", "prompt": "Rachel rode her red rocket to the stars.", "repetitions": 3}
                ]
            }
        ]
    },
    "S": {
        "title": "Sibilant /s/ Airflow & Alignment Protocol",
        "description": "Correcting frontal or lateral lisps by establishing central alveolar groove airstream.",
        "difficulty": "beginner",
        "phases": [
            {
                "phase": 1,
                "name": "Phase 1: Sound in Isolation",
                "target": "/s/",
                "goal": "Produce steady alveolar hissing airflow without tongue protrusion.",
                "status": "in_progress",
                "exercises": [
                    {"type": "cue", "instruction": "Make the hissing snake sound: /sss/!", "target": "S", "repetitions": 10},
                    {"type": "mouth_guidance", "instruction": "Keep teeth closed like a cage. Tongue tip stays behind top teeth.", "target": "S"}
                ]
            },
            {
                "phase": 2,
                "name": "Phase 2: Syllable Shapes",
                "target": "/s/ Syllables",
                "goal": "Syllable blending with high front vowels.",
                "status": "locked",
                "exercises": [
                    {"type": "drill", "prompt": "See", "target": "S IY", "repetitions": 5},
                    {"type": "drill", "prompt": "Say", "target": "S EY", "repetitions": 5},
                    {"type": "drill", "prompt": "So", "target": "S OW", "repetitions": 5},
                    {"type": "drill", "prompt": "Sun", "target": "S AH N", "repetitions": 5}
                ]
            },
            {
                "phase": 3,
                "name": "Phase 3: Word Level",
                "target": "Target /s/ Words",
                "goal": "Produce /s/ words in initial, medial, and final positions.",
                "status": "locked",
                "exercises": [
                    {"type": "word", "prompt": "Sun", "target": "S AH N", "repetitions": 5},
                    {"type": "word", "prompt": "Star", "target": "S T AA R", "repetitions": 5},
                    {"type": "word", "prompt": "Sand", "target": "S AE N D", "repetitions": 5},
                    {"type": "word", "prompt": "House", "target": "HH AW S", "repetitions": 5}
                ]
            },
            {
                "phase": 4,
                "name": "Phase 4: Carrier Sentences",
                "target": "Sentence Fluency",
                "goal": "Generalize central airflow into connected speech.",
                "status": "locked",
                "exercises": [
                    {"type": "sentence", "prompt": "I see seven stars in the sky.", "repetitions": 3},
                    {"type": "sentence", "prompt": "Sam sits in the summer sun.", "repetitions": 3}
                ]
            }
        ]
    },
    "K": {
        "title": "Velar /k/ Back-Tongue Elevation Curriculum",
        "description": "Remediating velar fronting (/k/ -> /t/) by strengthening posterior tongue occlusion.",
        "difficulty": "beginner",
        "phases": [
            {
                "phase": 1,
                "name": "Phase 1: Back Sound Isolation",
                "target": "/k/",
                "goal": "Produce 10 velar bursts with tongue tip depressed behind lower incisors.",
                "status": "in_progress",
                "exercises": [
                    {"type": "cue", "instruction": "Make the little cough sound: /k-k-k/!", "target": "K", "repetitions": 10},
                    {"type": "mouth_guidance", "instruction": "Rest tongue tip on the floor of your mouth. Lift back of tongue to soft roof.", "target": "K"}
                ]
            },
            {
                "phase": 2,
                "name": "Phase 2: Syllable Formation",
                "target": "/k/ Syllables",
                "goal": "Combine /k/ with varied vowel contexts.",
                "status": "locked",
                "exercises": [
                    {"type": "drill", "prompt": "Kay", "target": "K EY", "repetitions": 5},
                    {"type": "drill", "prompt": "Key", "target": "K IY", "repetitions": 5},
                    {"type": "drill", "prompt": "Koo", "target": "K UW", "repetitions": 5}
                ]
            },
            {
                "phase": 3,
                "name": "Phase 3: Core Vocabulary",
                "target": "/k/ Words",
                "goal": "Prevent alveolar substitution during word production.",
                "status": "locked",
                "exercises": [
                    {"type": "word", "prompt": "Cat", "target": "K AE T", "repetitions": 5},
                    {"type": "word", "prompt": "Cup", "target": "K AH P", "repetitions": 5},
                    {"type": "word", "prompt": "Kite", "target": "K AY T", "repetitions": 5}
                ]
            },
            {
                "phase": 4,
                "name": "Phase 4: Connected Phrases",
                "target": "Sentence Fluency",
                "goal": "Consistently produce velar sounds in sentences.",
                "status": "locked",
                "exercises": [
                    {"type": "sentence", "prompt": "Ken flew a cool blue kite.", "repetitions": 3},
                    {"type": "sentence", "prompt": "Keep the cup on the clean kitchen counter.", "repetitions": 3}
                ]
            }
        ]
    }
}

def _words_with_phoneme(phoneme: str, n: int = 3) -> list[str]:
    try:
        import pronouncing
        words = [w for w in pronouncing.search(rf"\\b{phoneme}\\b") if w.isalpha() and 3 <= len(w) <= 6]
        words.sort(key=len)
        return words[:n] or []
    except Exception:
        return []


def generate_therapy_plan(target_phoneme: str, child_id: int, difficulty: str = "beginner") -> dict:
    """
    Generates a personalized therapy curriculum for the child based on their target error sound.
    Falls back gracefully to a structured template for any phoneme.
    """
    clean_p = target_phoneme.strip("/").upper()
    
    if clean_p in THERAPY_CURRICULA:
        plan = dict(THERAPY_CURRICULA[clean_p])
        plan["child_id"] = child_id
        plan["target_phoneme"] = clean_p
        return plan

    # Generic evidence-based curriculum template
    art = get_phoneme_articulation(clean_p)
    return {
        "child_id": child_id,
        "target_phoneme": clean_p,
        "title": f"Targeted /{clean_p}/ Mastery Curriculum",
        "description": f"Personalized 4-phase program designed to habituate accurate /{clean_p}/ production.",
        "difficulty": difficulty,
        "phases": [
            {
                "phase": 1,
                "name": f"Phase 1: /{clean_p}/ in Isolation",
                "target": f"/{clean_p}/",
                "goal": f"Produce the /{clean_p}/ sound in isolation with proper motor placement.",
                "status": "in_progress",
                "exercises": [
                    {"type": "cue", "instruction": art["child_cue"], "target": clean_p, "repetitions": 10},
                    {"type": "mouth_guidance", "instruction": art["tongue_placement"], "target": clean_p}
                ]
            },
            {
                "phase": 2,
                "name": f"Phase 2: /{clean_p}/ Syllable Drills",
                "target": f"/{clean_p}/ + Vowels",
                "goal": f"Connect /{clean_p}/ with diverse vowel nuclei.",
                "status": "locked",
                "exercises": [
                    {"type": "drill", "prompt": f"{clean_p}-AY", "repetitions": 5},
                    {"type": "drill", "prompt": f"{clean_p}-EE", "repetitions": 5},
                    {"type": "drill", "prompt": f"{clean_p}-OH", "repetitions": 5}
                ]
            },
            {
                "phase": 3,
                "name": f"Phase 3: /{clean_p}/ Target Words",
                "target": f"Words containing /{clean_p}/",
                "goal": f"Accurately pronounce words with /{clean_p}/.",
                "status": "locked",
                "exercises": [
                    *[{"type": "word", "prompt": w, "repetitions": 5}
                      for w in (_words_with_phoneme(clean_p) or [f"a word with /{clean_p}/"])]
                ]
            },
            {
                "phase": 4,
                "name": f"Phase 4: Sentence Fluency",
                "target": "Connected Sentences",
                "goal": f"Generalize correct /{clean_p}/ into full sentences.",
                "status": "locked",
                "exercises": [
                    {"type": "sentence", "prompt": f"Practice saying short sentences with /{clean_p}/ clearly.", "repetitions": 3}
                ]
            }
        ]
    }
