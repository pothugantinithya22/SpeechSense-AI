import json
from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models.schemas import TherapistNoteCreate
from app.services.clinical_ai import generate_clinical_recommendations

router = APIRouter(prefix="/api/therapist", tags=["Therapist Clinical Dashboard"])

@router.get("/patients")
def get_therapist_patients(therapist_id: int = Query(1)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT c.id as child_id, c.age, c.diagnosis, c.avatar, c.stars, c.streak_days,
           c.last_practice_date, u.full_name, u.email
    FROM child_profiles c
    JOIN users u ON c.user_id = u.id
    ORDER BY c.id ASC
    """)
    rows = cursor.fetchall()
    
    patients = []
    for r in rows:
        cid = r["child_id"]
        # Fetch session count & average accuracy
        cursor.execute("SELECT AVG(accuracy), COUNT(id) FROM practice_sessions WHERE child_id = ?", (cid,))
        stats = cursor.fetchone()
        avg_acc = round(stats[0], 1) if stats and stats[0] is not None else 0.0
        session_count = stats[1] if stats else 0
        
        patients.append({
            "child_id": cid,
            "name": r["full_name"],
            "age": r["age"],
            "diagnosis": r["diagnosis"],
            "avatar": r["avatar"],
            "stars": r["stars"],
            "streak_days": r["streak_days"],
            "last_practice_date": r["last_practice_date"],
            "average_accuracy": avg_acc,
            "session_count": session_count,
            "parent_email": r["email"]
        })
        
    conn.close()
    return patients

@router.get("/patient/{child_id}")
def get_patient_detail(child_id: int):
    conn = get_db()
    cursor = conn.cursor()

    # Child info
    cursor.execute("""
    SELECT c.id as child_id, c.age, c.diagnosis, c.avatar, c.stars, c.streak_days,
           c.last_practice_date, u.full_name, u.email
    FROM child_profiles c
    JOIN users u ON c.user_id = u.id
    WHERE c.id = ?
    """, (child_id,))
    child = cursor.fetchone()
    if not child:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found.")

    # Sessions
    cursor.execute("""
    SELECT id, target_word, transcript, detected_phonemes, expected_phonemes,
           accuracy, per, error_count, created_at
    FROM practice_sessions
    WHERE child_id = ?
    ORDER BY id DESC
    """, (child_id,))
    sessions = [dict(s) for s in cursor.fetchall()]

    # Clinical notes
    cursor.execute("""
    SELECT tn.id, tn.note_text, tn.clinical_recommendations, tn.created_at, u.full_name as therapist_name
    FROM therapist_notes tn
    JOIN users u ON tn.therapist_id = u.id
    WHERE tn.child_id = ?
    ORDER BY tn.id DESC
    """, (child_id,))
    notes = [dict(n) for n in cursor.fetchall()]

    # Phoneme breakdown
    cursor.execute("""
    SELECT pr.expected_phoneme, AVG(pr.accuracy) as avg_acc
    FROM phoneme_results pr
    JOIN practice_sessions ps ON pr.session_id = ps.id
    WHERE ps.child_id = ? AND pr.expected_phoneme != '-'
    GROUP BY pr.expected_phoneme
    """, (child_id,))
    phoneme_stats = {r["expected_phoneme"]: round(r["avg_acc"], 1) for r in cursor.fetchall()}

    # Therapy Plan
    cursor.execute("""
    SELECT id, target_phoneme, title, current_phase, total_phases, status, exercises_json
    FROM therapy_plans
    WHERE child_id = ? AND status = 'active'
    ORDER BY id DESC LIMIT 1
    """, (child_id,))
    plan_row = cursor.fetchone()
    plan_data = None
    if plan_row:
        plan_data = json.loads(plan_row["exercises_json"])
        plan_data["id"] = plan_row["id"]
        plan_data["current_phase"] = plan_row["current_phase"]
        plan_data["total_phases"] = plan_row["total_phases"]

    conn.close()

    # AI recommendations
    ai_recom = generate_clinical_recommendations(
        child_name=child["full_name"],
        diagnosis=child["diagnosis"],
        sessions=sessions,
        phoneme_stats=phoneme_stats
    )

    return {
        "patient": dict(child),
        "sessions": sessions,
        "notes": notes,
        "phoneme_stats": phoneme_stats,
        "therapy_plan": plan_data,
        "ai_recommendations": ai_recom
    }

@router.post("/notes")
def add_clinical_note(data: TherapistNoteCreate, therapist_id: int = Query(1)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO therapist_notes (child_id, therapist_id, session_id, note_text, clinical_recommendations)
    VALUES (?, ?, ?, ?, ?)
    """, (data.child_id, therapist_id, data.session_id, data.note_text, data.clinical_recommendations))
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"status": "saved", "note_id": note_id, "message": "Clinical note saved successfully."}

@router.get("/recommendations/{child_id}")
def get_recommendations(child_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.diagnosis, u.full_name FROM child_profiles c JOIN users u ON c.user_id = u.id WHERE c.id = ?
    """, (child_id,))
    child = cursor.fetchone()
    if not child:
        conn.close()
        raise HTTPException(status_code=404, detail="Child not found.")

    cursor.execute("SELECT accuracy, per, created_at FROM practice_sessions WHERE child_id = ?", (child_id,))
    sessions = [dict(s) for s in cursor.fetchall()]

    cursor.execute("""
    SELECT pr.expected_phoneme, AVG(pr.accuracy) as avg_acc
    FROM phoneme_results pr
    JOIN practice_sessions ps ON pr.session_id = ps.id
    WHERE ps.child_id = ? AND pr.expected_phoneme != '-'
    GROUP BY pr.expected_phoneme
    """, (child_id,))
    phoneme_stats = {r["expected_phoneme"]: round(r["avg_acc"], 1) for r in cursor.fetchall()}
    conn.close()

    return generate_clinical_recommendations(
        child_name=child["full_name"],
        diagnosis=child["diagnosis"],
        sessions=sessions,
        phoneme_stats=phoneme_stats
    )
