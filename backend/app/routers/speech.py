import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.services.audio_preprocessor import preprocess_audio_detailed
from app.services.similarity import phoneme_similarity, similarity_score
from app.services.personalization import build_personalized_plan
from app.services.alignment import word_to_phonemes, calculate_metrics
from app.models.hubert_pipeline import decode_with_mode, get_pipeline_status
from app.services.explainable_ai import generate_xai_explanation
from app.services.visual_mouth_data import get_phoneme_articulation
from app.database import get_db
from app.config import HF_MODEL_REPO, HF_MODEL_FILE, DEVICE

router = APIRouter(prefix="/api/speech", tags=["Speech & Pronunciation Assessment"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SpeechSense AI Engine",
        "model_repo": HF_MODEL_REPO,
        "model_file": HF_MODEL_FILE,
        "device": str(DEVICE),
        "pipeline": "HuBERT Large CTC + CMUDict Alignment + Explainable AI",
        "active_mode": get_pipeline_status()
    }

@router.post("/analyze")
async def analyze_speech(
    audio: UploadFile = File(...),
    target_word: str = Form(...),
    child_id: int = Form(None)
):
    clean_target = target_word.strip()
    if not clean_target:
        raise HTTPException(status_code=400, detail="Target word or phrase is required.")

    raw_bytes = await audio.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Audio file data is empty.")

    # 1. Preprocess audio
    try:
        waveform, prep_info = preprocess_audio_detailed(raw_bytes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audio preprocessing error: {exc}")

    # 2. Extract expected CMU phonemes
    expected_phonemes = word_to_phonemes(clean_target)
    if not expected_phonemes:
        raise HTTPException(
            status_code=400,
            detail="The target text has no readable letters. Type a word, name, sentence or paragraph in English letters."
        )

    # 3. HuBERT Feature Extraction & CTC Phoneme Decoding
    try:
        decoded = decode_with_mode(waveform, clean_target)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Speech model unavailable: {exc}")
    detected_phonemes = decoded["phonemes"]
    confidences = decoded["confidences"]
    timestamps = decoded.get("timestamps") or []

    # 4. Levenshtein Alignment & Error Calculation
    metrics = calculate_metrics(expected_phonemes, detected_phonemes)
    alignment = metrics["alignment"]
    accuracy = metrics["accuracy"]
    per_raw = metrics["per"]
    per = min(per_raw, 100.0)   # PER can exceed 100% when many extra sounds are heard; show max 100%
    sim_score = similarity_score(alignment)

    # 5. Explainable AI (XAI) & Detailed Error Mapping
    phoneme_errors = []
    all_phonemes = []
    feedback_items = []
    xai_diagnostics_map = {}

    det_idx = 0  # position in detected_phonemes (omissions have no detected phoneme)
    for item in alignment:
        raw_exp = item["raw_expected"]
        raw_det = item["raw_detected"]
        status = item["status"]
        if raw_det != "-":
            conf = confidences[det_idx] if det_idx < len(confidences) else 0.85
            ts = timestamps[det_idx] if det_idx < len(timestamps) else None
            det_idx += 1
        else:
            conf = 0.85
            ts = None
        start_sec, end_sec = (ts[0], ts[1]) if ts else (None, None)   # error localization
        if status == "correct":
            sim = 100.0
        elif status == "substitution":
            sim = round(phoneme_similarity(raw_exp, raw_det) * 100, 1)
        else:
            sim = 0.0

        if status == "correct":
            all_phonemes.append({
                "ph": f"/{raw_exp}/",
                "acc": 100.0,
                "err": "Correct",
                "words": clean_target,
                "confidence": round(conf * 100, 1),
                "similarity": sim,
                "start_sec": start_sec,
                "end_sec": end_sec
            })
        else:
            acc_val = 0.0
            err_label = f"Substitution (/{raw_det}/)" if status == "substitution" else status.capitalize()
            all_phonemes.append({
                "ph": f"/{raw_exp}/" if raw_exp != "-" else f"/{raw_det}/",
                "acc": acc_val,
                "err": err_label,
                "words": clean_target,
                "confidence": round(conf * 100, 1),
                "similarity": sim,
                "start_sec": start_sec,
                "end_sec": end_sec
            })

            # Generate XAI explanation
            xai_diag = generate_xai_explanation(raw_exp, raw_det, conf)
            xai_key = raw_exp if raw_exp != "-" else f"+{raw_det}"
            xai_diagnostics_map[xai_key] = xai_diag

            art = get_phoneme_articulation(raw_exp if raw_exp != "-" else raw_det)
            phoneme_errors.append({
                "word": clean_target,
                "phoneme": f"/{raw_exp}/" if raw_exp != "-" else f"(extra /{raw_det}/)",
                "type": status,
                "produced": f"/{raw_det}/" if raw_det != "-" else "(missed)",
                "expected": raw_exp,
                "detected": raw_det if raw_det != "-" else None,
                "accuracy": acc_val,
                "confidence": round(conf * 100, 1),
                "similarity": sim,
                "start_sec": start_sec,
                "end_sec": end_sec,
                "tip_title": art.get("manner", "Articulatory Guidance"),
                "tip": art.get("child_cue", "Practice slowly with proper mouth placement."),
                "xai_explanation": xai_diag["why_flagged"]
            })

            feedback_items.append({
                "phoneme": raw_exp if raw_exp != "-" else raw_det,
                "phoneme_label": f"/{raw_exp}/" if raw_exp != "-" else f"(extra /{raw_det}/)",
                "title": art.get("manner", "Articulatory Placement"),
                "tip": art.get("child_cue", ""),
                "therapist_cue": art.get("therapist_note", ""),
                "issue": status,
                "xai": xai_diag
            })

    # 6. Overall Performance Summary
    if accuracy >= 90:
        grade = "Excellent Mastery"
        emoji = "star"
        msg = "Flawless pronunciation matching target articulatory acoustics!"
    elif accuracy >= 70:
        grade = "Good Progress"
        emoji = "thumbs-up"
        msg = "Intelligible production with minor phoneme variance."
    elif accuracy >= 45:
        grade = "Emerging Target"
        emoji = "practice"
        msg = "Sound awareness present; focus on articulatory posture cues."
    else:
        grade = "Practice Needed"
        emoji = "retry"
        msg = "Noticeable substitution or omission; review visual mouth model."

    summary = {
        "grade": grade,
        "emoji": emoji,
        "message": msg
    }

    # 7. Actionable Recommendations
    recommendations = []
    if phoneme_errors:
        for err in phoneme_errors[:2]:
            recommendations.append(f"Review visual mouth guidance for {err['phoneme']}: {err['tip']}")
        recommendations.append(f"Repeat target word '{clean_target}' 3 times at half-speed.")
    else:
        recommendations.append(f"Great job! Generalize '{clean_target}' into a full descriptive sentence.")
    recommendations.append("Log your attempt in the Child Dashboard to build your streak!")

    # 8. Persist to Database if child_id provided
    session_id = None
    if child_id:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO practice_sessions (child_id, target_word, transcript, detected_phonemes, expected_phonemes, accuracy, per, error_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                child_id,
                clean_target,
                f"Practice attempt for {clean_target}",
                json.dumps(detected_phonemes),
                json.dumps(expected_phonemes),
                accuracy,
                per,
                len(phoneme_errors)
            ))
            session_id = cursor.lastrowid

            for exp_p in metrics["alignment"]:
                cursor.execute("""
                INSERT INTO phoneme_results (session_id, expected_phoneme, detected_phoneme, status, accuracy, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, exp_p["raw_expected"], exp_p["raw_detected"], exp_p["status"], 100.0 if exp_p["status"] == "correct" else 0.0, 0.90))

            # Add stars to child profile (+3 stars for attempt, +5 if > 80% accuracy)
            earned_stars = 5 if accuracy >= 80 else 3
            cursor.execute("""
            UPDATE child_profiles
            SET stars = stars + ?,
                streak_days = CASE WHEN last_practice_date = CURRENT_DATE THEN streak_days ELSE streak_days + 1 END,
                last_practice_date = CURRENT_DATE
            WHERE id = ?
            """, (earned_stars, child_id))

            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"Database persistence notice: {db_err}")

    # 9. Personalized therapy plan (weak sounds -> difficulty -> exercises)
    try:
        personalized_plan = build_personalized_plan(child_id, alignment, accuracy)
    except Exception as plan_err:
        print(f"Personalization notice: {plan_err}")
        personalized_plan = {"weak_sounds": [], "difficulty": "beginner", "plan_title": None,
                             "next_exercises": [], "message": ""}
    if personalized_plan.get("message"):
        recommendations.insert(0, personalized_plan["message"])

    # 10. Pipeline trace (mirrors the methodology: input -> preprocessing -> features -> assessment -> XAI -> plan -> dashboard)
    mode_labels = {
        "hubert_phoneme": "HuBERT Large + CTC phoneme head (trained checkpoint)",
        "hubert_asr": "HuBERT Large speech recognition + CMU phoneme conversion",
        "demo_fallback": "DEMO heuristic (no neural model loaded)",
    }
    n_words = len(clean_target.split())
    weak_txt = ", ".join(f"/{w['phoneme']}/" for w in personalized_plan["weak_sounds"]) or "none"
    pipeline = [
        {"stage": "Speech Input", "detail": f"{n_words} target word(s) · {prep_info.get('duration_sec', 0)} s of audio"},
        {"stage": "Data Preprocessing", "detail": (
            f"Resampled to 16 kHz · noise reduction {'on' if prep_info.get('noise_reduced') else 'off'} · "
            f"{len(prep_info.get('segments', []))} speech segment(s)")},
        {"stage": "Feature Extraction", "detail": mode_labels.get(decoded["mode"], decoded["mode"])},
        {"stage": "Pronunciation Assessment", "detail": (
            f"{len(detected_phonemes)} phonemes heard · accuracy {accuracy}% · PER {per}% · similarity {sim_score}%")},
        {"stage": "Explainable AI & Visual Guidance", "detail": f"{len(phoneme_errors)} error(s) explained with mouth guidance"},
        {"stage": "Personalized Therapy Plan", "detail": f"Weak sounds: {weak_txt} · {personalized_plan['difficulty']} level"},
        {"stage": "Therapist Intelligence Dashboard",
         "detail": "Session saved to the child's progress" if session_id else "Log in as a child to save progress to the dashboard"},
    ]

    return {
        "target_word": clean_target,
        "expected_phonemes": expected_phonemes,
        "detected_phonemes": detected_phonemes,
        "alignment": alignment,
        "phoneme_errors": phoneme_errors,
        "feedback": feedback_items,
        "all_phonemes": all_phonemes,
        "accuracy": accuracy,
        "per": per,
        "per_raw": per_raw,
        "similarity_score": sim_score,
        "preprocessing": prep_info,
        "personalized_plan": personalized_plan,
        "pipeline": pipeline,
        "summary": summary,
        "recommendations": recommendations,
        "xai_diagnostics": xai_diagnostics_map,
        "session_id": session_id,
        "mode": decoded["mode"],
        "transcript": decoded["transcript"],
        "warning": decoded["warning"]
    }
