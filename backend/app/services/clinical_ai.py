"""
Clinical AI Service for Therapist Insights & Clinical Recommendations.
Analyzes longitudinal patient data and generates diagnostic summaries and intervention plans.
"""

def generate_clinical_recommendations(child_name: str, diagnosis: str, sessions: list[dict], phoneme_stats: dict) -> dict:
    """
    Generates structured clinical recommendations and diagnostic summary for an SLP.
    """
    total_sessions = len(sessions)
    if total_sessions == 0:
        return {
            "summary": f"Initial clinical evaluation pending for {child_name}. No recorded sessions yet.",
            "recommendations": [
                "Administer baseline speech assessment using initial consonant inventory.",
                "Establish therapeutic rapport and introduce the Visual Articulation tool."
            ],
            "severity_index": "Assessment Phase",
            "suggested_frequency": "2x weekly, 30 minutes",
            "home_practice_target": "5-10 minutes daily with parent supervision"
        }

    avg_acc = sum(s.get("accuracy", 0.0) for s in sessions) / total_sessions
    recent_acc = sessions[-1].get("accuracy", 0.0) if sessions else avg_acc

    # Identify phonemes with lowest mastery
    struggling_phonemes = [
        phone for phone, score in phoneme_stats.items()
        if score < 75.0
    ]

    # Clinical determination
    if avg_acc >= 85.0:
        severity = "Mild / Approaching Graduation"
        freq = "1x weekly or bi-weekly check-in"
    elif avg_acc >= 65.0:
        severity = "Moderate Speech Sound Disorder"
        freq = "2x weekly, 30-minute sessions"
    else:
        severity = "Significant / High Impact Disorder"
        freq = "2-3x weekly intensive therapy"

    recommendations = []
    if struggling_phonemes:
        p_list = ", ".join(f"/{p}/" for p in struggling_phonemes[:3])
        recommendations.append(f"Prioritize articulatory motor drills for {p_list}.")
        recommendations.append(f"Utilize real-time Visual Articulation biofeedback to prevent habitual substitution.")
    else:
        recommendations.append("Continue maintenance exercises across multi-syllabic carrier sentences.")

    if recent_acc > avg_acc:
        trend_note = f"Positive clinical trajectory: recent performance ({recent_acc:.1f}%) exceeds historical baseline ({avg_acc:.1f}%)."
    else:
        trend_note = f"Plateau observed: recent performance ({recent_acc:.1f}%) suggests reviewing isolation cues."

    recommendations.append("Assign home practice through the Child Dashboard targeting high-frequency functional vocabulary.")
    recommendations.append("Conduct monthly acoustic phoneme re-evaluation to measure PER reduction.")

    return {
        "summary": f"{child_name} ({diagnosis}) has completed {total_sessions} logged practice sessions with an overall mean accuracy of {avg_acc:.1f}%. {trend_note}",
        "severity_index": severity,
        "suggested_frequency": freq,
        "struggling_phonemes": struggling_phonemes,
        "recommendations": recommendations,
        "home_practice_target": "10 minutes daily using the gamified practice module"
    }
