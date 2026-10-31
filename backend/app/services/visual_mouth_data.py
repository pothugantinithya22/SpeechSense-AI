"""
Articulatory and Anatomical Guidance Data for CMU Phonemes.
Provides precise physical positioning data for interactive 2D sagittal cross-section
and frontal mouth rendering, accompanied by evidence-based speech-language cues.
"""

PHONEME_ARTICULATION_DATA = {
    "R": {
        "symbol": "/r/",
        "manner": "Liquid (Approximant / Rhotic)",
        "place": "Postalveolar / Palatal",
        "voicing": "Voiced",
        "lip_shape": "Slightly unrounded / relaxed neutral",
        "tongue_placement": "Tongue blade retracted into retroflex curl or bunched against posterior upper molars.",
        "airflow": "Smooth central non-turbulent oral airflow without friction.",
        "child_cue": "Make the growling bear sound /rrr/! Keep your lips smiling slightly so they don't turn into a round /w/.",
        "therapist_note": "Acoustically marked by a sharply depressed F3 frequency (< 2000 Hz). Encourage lateral tongue bracing against maxillary molars.",
        "svg_params": {
            "tongue_tip_x": 135,
            "tongue_tip_y": 120,
            "tongue_body_x": 115,
            "tongue_body_y": 140,
            "lips_open": 20,
            "lip_rounding": 10,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "palate_and_blade"
        }
    },
    "W": {
        "symbol": "/w/",
        "manner": "Glide",
        "place": "Labio-velar",
        "voicing": "Voiced",
        "lip_shape": "Tightly rounded / puckered circle",
        "tongue_placement": "Tongue dorsum raised toward velum; tongue tip remains low and relaxed.",
        "airflow": "Central smooth glide as lips rapidly open.",
        "child_cue": "Pucker your lips like you are blowing a bubble!",
        "therapist_note": "Characterized by low F1 and F2 formants with neutral or high F3. Distinguishable from /r/ by absence of low F3.",
        "svg_params": {
            "tongue_tip_x": 160,
            "tongue_tip_y": 155,
            "tongue_body_x": 100,
            "tongue_body_y": 115,
            "lips_open": 12,
            "lip_rounding": 40,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "lips_and_velum"
        }
    },
    "S": {
        "symbol": "/s/",
        "manner": "Fricative",
        "place": "Alveolar",
        "voicing": "Voiceless",
        "lip_shape": "Neutral to slight spread smile",
        "tongue_placement": "Tongue tip close behind the upper front alveolar ridge forming a narrow groove.",
        "airflow": "High-velocity friction stream hitting incisor edges.",
        "child_cue": "Make the hissing snake sound /sss/! Keep your teeth closed like a fence so the tongue snake doesn't peek out!",
        "therapist_note": "High spectral peak (> 4.5 kHz). Check for interdental placement causing frontal lisp (substitution with /th/).",
        "svg_params": {
            "tongue_tip_x": 165,
            "tongue_tip_y": 108,
            "tongue_body_x": 130,
            "tongue_body_y": 145,
            "lips_open": 10,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "alveolar_ridge"
        }
    },
    "TH": {
        "symbol": "/θ/",
        "manner": "Fricative",
        "place": "Interdental",
        "voicing": "Voiceless",
        "lip_shape": "Neutral / relaxed open",
        "tongue_placement": "Tongue tip protrudes gently between incisal edges of upper and lower teeth.",
        "airflow": "Diffuse turbulent airflow across the flat blade of the tongue.",
        "child_cue": "Gently bite your tongue sandwich between your teeth and blow soft cool air!",
        "therapist_note": "Flat, diffuse spectral noise lower in intensity than /s/ without high-frequency energy concentration.",
        "svg_params": {
            "tongue_tip_x": 182,
            "tongue_tip_y": 115,
            "tongue_body_x": 130,
            "tongue_body_y": 150,
            "lips_open": 18,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "incisors_interdental"
        }
    },
    "DH": {
        "symbol": "/ð/",
        "manner": "Fricative",
        "place": "Interdental",
        "voicing": "Voiced",
        "lip_shape": "Neutral",
        "tongue_placement": "Tongue tip between teeth with vocal folds buzzing.",
        "airflow": "Voiced friction through the dental aperture.",
        "child_cue": "Put your tongue between your teeth and turn your motor on to buzz!",
        "therapist_note": "Voiced counterpart to /th/. Watch for stopping substitution (/d/).",
        "svg_params": {
            "tongue_tip_x": 182,
            "tongue_tip_y": 115,
            "tongue_body_x": 130,
            "tongue_body_y": 150,
            "lips_open": 18,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "incisors_interdental"
        }
    },
    "L": {
        "symbol": "/l/",
        "manner": "Lateral Liquid",
        "place": "Alveolar",
        "voicing": "Voiced",
        "lip_shape": "Neutral",
        "tongue_placement": "Tongue tip firmly anchored to alveolar ridge; lateral sides depressed for bilateral air release.",
        "airflow": "Air passes laterally around both sides of the tongue.",
        "child_cue": "Sing like a singer: 'La-la-la!' Tap your tongue tip right behind your front top teeth.",
        "therapist_note": "High F2 and low F1 with characteristic lateral formant anti-resonances.",
        "svg_params": {
            "tongue_tip_x": 168,
            "tongue_tip_y": 105,
            "tongue_body_x": 125,
            "tongue_body_y": 150,
            "lips_open": 22,
            "lip_rounding": 5,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "alveolar_contact"
        }
    },
    "K": {
        "symbol": "/k/",
        "manner": "Stop / Plosive",
        "place": "Velar",
        "voicing": "Voiceless",
        "lip_shape": "Neutral open",
        "tongue_placement": "Tongue back (dorsum) raises to firmly occlude the soft palate (velum), building intraoral pressure.",
        "airflow": "Sudden unvoiced burst release after total velar closure.",
        "child_cue": "Cough sound /k-k-k/ from the back of your throat! Keep your tongue tip sleeping down.",
        "therapist_note": "Fronting error occurs when child substitutes alveolar /t/ for velar /k/. Emphasize posterior elevation.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 160,
            "tongue_body_x": 95,
            "tongue_body_y": 100,
            "lips_open": 25,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "velum_contact"
        }
    },
    "G": {
        "symbol": "/g/",
        "manner": "Stop / Plosive",
        "place": "Velar",
        "voicing": "Voiced",
        "lip_shape": "Neutral open",
        "tongue_placement": "Tongue dorsum seals against velum with vocal cord vibration during closure.",
        "airflow": "Voiced plosive burst released from soft palate.",
        "child_cue": "Make the drinking gulp sound /g-g-g/ with your voice on!",
        "therapist_note": "Voiced cognate of /k/. Target for velar fronting remediation.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 160,
            "tongue_body_x": 95,
            "tongue_body_y": 100,
            "lips_open": 25,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "velum_contact"
        }
    },
    "T": {
        "symbol": "/t/",
        "manner": "Stop / Plosive",
        "place": "Alveolar",
        "voicing": "Voiceless",
        "lip_shape": "Neutral",
        "tongue_placement": "Tongue tip seals against alveolar ridge, occluding breath, then pops open.",
        "airflow": "Explosive burst of unvoiced air.",
        "child_cue": "Make the ticking clock sound /t-t-t/! Tap your tongue tip behind top teeth.",
        "therapist_note": "Aspiration burst following silent stop interval.",
        "svg_params": {
            "tongue_tip_x": 170,
            "tongue_tip_y": 105,
            "tongue_body_x": 125,
            "tongue_body_y": 145,
            "lips_open": 18,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "alveolar_ridge"
        }
    },
    "D": {
        "symbol": "/d/",
        "manner": "Stop / Plosive",
        "place": "Alveolar",
        "voicing": "Voiced",
        "lip_shape": "Neutral",
        "tongue_placement": "Tongue tip against alveolar ridge with voice on.",
        "airflow": "Voiced plosive release.",
        "child_cue": "Drum sound /d-d-d/! Tap your tongue with your voice humming.",
        "therapist_note": "Voiced alveolar stop with low voice bar during closure.",
        "svg_params": {
            "tongue_tip_x": 170,
            "tongue_tip_y": 105,
            "tongue_body_x": 125,
            "tongue_body_y": 145,
            "lips_open": 18,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "alveolar_ridge"
        }
    },
    "SH": {
        "symbol": "/ʃ/",
        "manner": "Fricative",
        "place": "Postalveolar",
        "voicing": "Voiceless",
        "lip_shape": "Rounded and slightly flared/projected",
        "tongue_placement": "Tongue blade raised toward postalveolar region; sides braced against upper bicuspids.",
        "airflow": "Broad turbulent unvoiced noise.",
        "child_cue": "Quiet baby sound /shhh/! Flare your lips out like a trumpet horn.",
        "therapist_note": "Broader spectral energy than /s/, centered between 2.5 and 4.5 kHz.",
        "svg_params": {
            "tongue_tip_x": 150,
            "tongue_tip_y": 112,
            "tongue_body_x": 120,
            "tongue_body_y": 140,
            "lips_open": 16,
            "lip_rounding": 30,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "postalveolar"
        }
    },
    "CH": {
        "symbol": "/tʃ/",
        "manner": "Affricate",
        "place": "Postalveolar",
        "voicing": "Voiceless",
        "lip_shape": "Rounded and projected",
        "tongue_placement": "Stop closure at postalveolar ridge transitioning rapidly to turbulent friction.",
        "airflow": "Burst followed immediately by postalveolar friction.",
        "child_cue": "Train engine /ch-ch-ch/! Start with a tap, then sneeze air through flared lips.",
        "therapist_note": "Combined /t/ occlusion followed by rapid /sh/ friction release.",
        "svg_params": {
            "tongue_tip_x": 155,
            "tongue_tip_y": 108,
            "tongue_body_x": 120,
            "tongue_body_y": 140,
            "lips_open": 18,
            "lip_rounding": 25,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "postalveolar"
        }
    },
    "F": {
        "symbol": "/f/",
        "manner": "Fricative",
        "place": "Labiodental",
        "voicing": "Voiceless",
        "lip_shape": "Bottom lip tucked slightly against top incisors",
        "tongue_placement": "Tongue relaxed in low-central oral cavity.",
        "airflow": "Continuous breath passing through the upper teeth and lower lip constriction.",
        "child_cue": "Bite your bottom lip gently and blow air like a gentle breeze /fff/!",
        "therapist_note": "Low intensity high-frequency noise with diffuse spectral profile.",
        "svg_params": {
            "tongue_tip_x": 145,
            "tongue_tip_y": 150,
            "tongue_body_x": 120,
            "tongue_body_y": 155,
            "lips_open": 12,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "labiodental_teeth_lip"
        }
    },
    "V": {
        "symbol": "/v/",
        "manner": "Fricative",
        "place": "Labiodental",
        "voicing": "Voiced",
        "lip_shape": "Bottom lip against upper incisors",
        "tongue_placement": "Tongue resting low in mouth.",
        "airflow": "Voiced friction buzzing between lower lip and upper teeth.",
        "child_cue": "Car motor sound /vvv/! Feel your bottom lip tickle against your top teeth.",
        "therapist_note": "Voiced labiodental fricative with periodic vocal fold excitation.",
        "svg_params": {
            "tongue_tip_x": 145,
            "tongue_tip_y": 150,
            "tongue_body_x": 120,
            "tongue_body_y": 155,
            "lips_open": 12,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "labiodental_teeth_lip"
        }
    },
    "B": {
        "symbol": "/b/",
        "manner": "Stop / Plosive",
        "place": "Bilabial",
        "voicing": "Voiced",
        "lip_shape": "Both lips closed firmly together",
        "tongue_placement": "Tongue relaxed low in oral cavity.",
        "airflow": "Intraoral pressure built behind bilabial seal, then popped open with voice.",
        "child_cue": "Press your lips together like a tight package, then POP with your voice on!",
        "therapist_note": "Bilabial voiced stop showing voice bar preceding plosive transient.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 150,
            "tongue_body_x": 120,
            "tongue_body_y": 155,
            "lips_open": 0,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "bilabial_lips"
        }
    },
    "P": {
        "symbol": "/p/",
        "manner": "Stop / Plosive",
        "place": "Bilabial",
        "voicing": "Voiceless",
        "lip_shape": "Lips firmly pressed together",
        "tongue_placement": "Tongue neutral in mouth.",
        "airflow": "Silent pressure build-up popped open without voice.",
        "child_cue": "Popcorn sound /p-p-p/! Pop your lips without turning your throat voice on.",
        "therapist_note": "Voiceless bilabial plosive with prominent aspiration noise.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 150,
            "tongue_body_x": 120,
            "tongue_body_y": 155,
            "lips_open": 0,
            "lip_rounding": 0,
            "velum_closed": True,
            "vocal_folds_vibrating": False,
            "highlight_region": "bilabial_lips"
        }
    },
    "M": {
        "symbol": "/m/",
        "manner": "Nasal",
        "place": "Bilabial",
        "voicing": "Voiced",
        "lip_shape": "Lips closed together gently",
        "tongue_placement": "Tongue resting flat.",
        "airflow": "Velum lowers; sound resonates completely out through the nasal cavity.",
        "child_cue": "Yummy food sound /mmm/! Feel the tickle in your nose while your lips stay closed.",
        "therapist_note": "Nasal resonance with lowered velum, low primary nasal murmur ~250 Hz.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 155,
            "tongue_body_x": 120,
            "tongue_body_y": 160,
            "lips_open": 0,
            "lip_rounding": 0,
            "velum_closed": False,
            "vocal_folds_vibrating": True,
            "highlight_region": "nasal_cavity"
        }
    },
    "N": {
        "symbol": "/n/",
        "manner": "Nasal",
        "place": "Alveolar",
        "voicing": "Voiced",
        "lip_shape": "Neutral open",
        "tongue_placement": "Tongue tip seals against alveolar ridge; velum lowers.",
        "airflow": "Acoustic resonance directed through nasal cavity.",
        "child_cue": "Humming aeroplane sound /nnn/! Tap your tongue on the roof while air leaves your nose.",
        "therapist_note": "Alveolar nasal occlusion with lowered velum creating open velopharyngeal port.",
        "svg_params": {
            "tongue_tip_x": 170,
            "tongue_tip_y": 105,
            "tongue_body_x": 125,
            "tongue_body_y": 145,
            "lips_open": 18,
            "lip_rounding": 0,
            "velum_closed": False,
            "vocal_folds_vibrating": True,
            "highlight_region": "nasal_and_alveolar"
        }
    }
}

def get_phoneme_articulation(phoneme: str) -> dict:
    """Returns articulation data for a phoneme, with sensible fallbacks for vowels/unlisted phones."""
    clean = phoneme.strip("/").upper()
    if clean in PHONEME_ARTICULATION_DATA:
        return PHONEME_ARTICULATION_DATA[clean]

    # Default vowel / generic articulatory fallback
    return {
        "symbol": f"/{clean}/",
        "manner": "Vowel / Oral Sound",
        "place": "Central Oral Cavity",
        "voicing": "Voiced",
        "lip_shape": "Open vocal tract",
        "tongue_placement": "Tongue positioned in central acoustic resonance position.",
        "airflow": "Smooth unrestricted vocal resonance.",
        "child_cue": f"Open your mouth clearly and make the /{clean}/ sound with continuous voice!",
        "therapist_note": f"Standard vocalic resonance for phoneme {clean}.",
        "svg_params": {
            "tongue_tip_x": 140,
            "tongue_tip_y": 150,
            "tongue_body_x": 120,
            "tongue_body_y": 145,
            "lips_open": 25,
            "lip_rounding": 10,
            "velum_closed": True,
            "vocal_folds_vibrating": True,
            "highlight_region": "oral_cavity"
        }
    }
