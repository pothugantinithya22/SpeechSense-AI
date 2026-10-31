import json
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from app.database import get_db

router = APIRouter(prefix="/api/progress", tags=["Progress Tracking & Analytics"])

@router.get("/{child_id}")
def get_child_progress(child_id: int):
    conn = get_db()
    cursor = conn.cursor()

    # Child profile & user info
    cursor.execute("""
    SELECT c.id as child_id, c.age, c.diagnosis, c.avatar, c.stars, c.streak_days, u.full_name
    FROM child_profiles c
    JOIN users u ON c.user_id = u.id
    WHERE c.id = ?
    """, (child_id,))
    child = cursor.fetchone()
    if not child:
        conn.close()
        raise HTTPException(status_code=404, detail="Child profile not found.")

    # Sessions history
    cursor.execute("""
    SELECT id, target_word, transcript, detected_phonemes, expected_phonemes,
           accuracy, per, error_count, created_at
    FROM practice_sessions
    WHERE child_id = ?
    ORDER BY id ASC
    """, (child_id,))
    sessions = cursor.fetchall()

    session_list = []
    total_acc = 0.0
    total_per = 0.0

    for s in sessions:
        session_list.append({
            "id": s["id"],
            "target_word": s["target_word"],
            "accuracy": s["accuracy"],
            "per": s["per"],
            "error_count": s["error_count"],
            "created_at": s["created_at"]
        })
        total_acc += s["accuracy"]
        total_per += s["per"]

    total_sessions = len(session_list)
    avg_acc = round(total_acc / total_sessions, 1) if total_sessions > 0 else 0.0
    avg_per = round(total_per / total_sessions, 1) if total_sessions > 0 else 0.0

    # Phoneme breakdown across all sessions
    cursor.execute("""
    SELECT pr.expected_phoneme, pr.status, pr.accuracy
    FROM phoneme_results pr
    JOIN practice_sessions ps ON pr.session_id = ps.id
    WHERE ps.child_id = ?
    """, (child_id,))
    phoneme_records = cursor.fetchall()

    phoneme_scores = defaultdict(list)
    error_dist = {"substitution": 0, "omission": 0, "insertion": 0}

    for pr in phoneme_records:
        exp = pr["expected_phoneme"]
        status = pr["status"]
        if exp and exp != "-":
            phoneme_scores[exp].append(pr["accuracy"])
        if status in error_dist:
            error_dist[status] += 1

    # Compute average mastery per phoneme
    mastery = {}
    for phone, scores in phoneme_scores.items():
        mastery[phone] = round(sum(scores) / len(scores), 1)

    conn.close()

    return {
        "child_id": child["child_id"],
        "child_name": child["full_name"],
        "age": child["age"],
        "diagnosis": child["diagnosis"],
        "avatar": child["avatar"],
        "stars": child["stars"],
        "streak_days": child["streak_days"],
        "total_sessions": total_sessions,
        "average_accuracy": avg_acc,
        "average_per": avg_per,
        "phoneme_mastery": mastery,
        "recent_sessions": session_list[-10:],
        "all_sessions": session_list,
        "error_distribution": error_dist
    }
