import json
from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.services.therapy_generator import generate_therapy_plan
from app.models.schemas import TherapyGenerateRequest

router = APIRouter(prefix="/api/therapy", tags=["Personalized Therapy Plans"])

@router.get("/plan/{child_id}")
def get_therapy_plan(child_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, child_id, target_phoneme, title, description, difficulty,
           current_phase, total_phases, exercises_json, status, created_at
    FROM therapy_plans
    WHERE child_id = ? AND status = 'active'
    ORDER BY id DESC LIMIT 1
    """, (child_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        # Generate default plan for child if none exists
        default_plan = generate_therapy_plan("R", child_id, "beginner")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO therapy_plans (child_id, target_phoneme, title, description, difficulty, current_phase, total_phases, exercises_json, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (child_id, "R", default_plan["title"], default_plan["description"], default_plan["difficulty"], 1, 4, json.dumps(default_plan)))
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        default_plan["id"] = plan_id
        default_plan["current_phase"] = 1
        default_plan["total_phases"] = 4
        default_plan["status"] = "active"
        return default_plan

    plan_data = json.loads(row["exercises_json"])
    plan_data["id"] = row["id"]
    plan_data["child_id"] = row["child_id"]
    plan_data["target_phoneme"] = row["target_phoneme"]
    plan_data["title"] = row["title"]
    plan_data["description"] = row["description"]
    plan_data["difficulty"] = row["difficulty"]
    plan_data["current_phase"] = row["current_phase"]
    plan_data["total_phases"] = row["total_phases"]
    plan_data["status"] = row["status"]
    plan_data["created_at"] = row["created_at"]
    return plan_data

@router.post("/generate")
def create_therapy_plan(req: TherapyGenerateRequest):
    plan = generate_therapy_plan(req.target_phoneme, req.child_id, req.difficulty)
    conn = get_db()
    cursor = conn.cursor()
    
    # Deactivate previous active plans for this phoneme
    cursor.execute("""
    UPDATE therapy_plans SET status = 'archived' WHERE child_id = ? AND target_phoneme = ?
    """, (req.child_id, plan["target_phoneme"]))

    cursor.execute("""
    INSERT INTO therapy_plans (child_id, target_phoneme, title, description, difficulty, current_phase, total_phases, exercises_json, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        req.child_id,
        plan["target_phoneme"],
        plan["title"],
        plan["description"],
        plan["difficulty"],
        1,
        len(plan["phases"]),
        json.dumps(plan)
    ))
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()

    plan["id"] = plan_id
    plan["current_phase"] = 1
    plan["total_phases"] = len(plan["phases"])
    plan["status"] = "active"
    return plan

@router.post("/advance-phase/{plan_id}")
def advance_phase(plan_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT current_phase, total_phases, exercises_json FROM therapy_plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Therapy plan not found.")

    current = row["current_phase"]
    total = row["total_phases"]
    plan_data = json.loads(row["exercises_json"])

    if current < total:
        new_phase = current + 1
        # Update phase status in json
        for ph in plan_data.get("phases", []):
            if ph["phase"] == current:
                ph["status"] = "completed"
            elif ph["phase"] == new_phase:
                ph["status"] = "in_progress"

        cursor.execute("""
        UPDATE therapy_plans
        SET current_phase = ?, exercises_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (new_phase, json.dumps(plan_data), plan_id))
        conn.commit()
        conn.close()
        return {"status": "advanced", "current_phase": new_phase, "message": f"Congratulations! Advanced to Phase {new_phase}."}
    else:
        conn.close()
        return {"status": "completed", "current_phase": current, "message": "All curriculum phases already completed!"}
