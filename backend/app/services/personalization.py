"""Personalized therapy: identify weak sounds, choose difficulty, select exercises."""
from app.services.therapy_generator import generate_therapy_plan


def _difficulty(avg_accuracy: float) -> str:
    return "beginner" if avg_accuracy < 50 else "intermediate" if avg_accuracy < 75 else "advanced"


def build_personalized_plan(child_id, alignment, accuracy):
    weak, avg_acc = [], accuracy
    stats = {}
    try:
        if child_id:
            from app.database import get_db
            conn = get_db()
            rows = conn.execute("""
                SELECT pr.expected_phoneme AS ph, COUNT(*) AS total,
                       SUM(CASE WHEN pr.status != 'correct' THEN 1 ELSE 0 END) AS errors
                FROM phoneme_results pr JOIN practice_sessions ps ON ps.id = pr.session_id
                WHERE ps.child_id = ? AND pr.expected_phoneme != '-'
                GROUP BY pr.expected_phoneme""", (child_id,)).fetchall()
            for r in rows:
                stats[r["ph"]] = (r["total"], r["errors"])
            recent = conn.execute("SELECT accuracy FROM practice_sessions WHERE child_id = ? "
                                  "ORDER BY id DESC LIMIT 5", (child_id,)).fetchall()
            if recent:
                avg_acc = sum(r["accuracy"] for r in recent) / len(recent)
            conn.close()
    except Exception:
        stats = {}
    if not stats:  # no history: use only the current attempt
        for it in alignment:
            if it["raw_expected"] == "-":
                continue
            t, e = stats.get(it["raw_expected"], (0, 0))
            stats[it["raw_expected"]] = (t + 1, e + (it["status"] != "correct"))

    for ph, (total, errors) in stats.items():
        if errors:
            weak.append({"phoneme": ph, "attempts": total, "errors": errors,
                         "error_rate": round(errors / total * 100, 1)})
    # rank by error rate, but trust sounds with more attempts (1 attempt counts 1/5 as much as 5+)
    weak.sort(key=lambda w: (-(w["error_rate"] * min(w["attempts"], 5) / 5), -w["errors"]))
    weak = weak[:3]
    difficulty = _difficulty(avg_acc)

    if not weak:
        return {"weak_sounds": [], "difficulty": difficulty, "plan_title": None, "next_exercises": [],
                "message": "No weak sounds found - move on to longer words and full sentences."}
    plan = generate_therapy_plan(weak[0]["phoneme"], child_id or 0, difficulty)
    first = plan["phases"][0] if plan.get("phases") else {}
    return {
        "weak_sounds": weak,
        "difficulty": difficulty,
        "plan_title": plan.get("title"),
        "current_phase": first.get("name"),
        "next_exercises": first.get("exercises", [])[:3],
        "message": f"Focus on /{weak[0]['phoneme']}/ first ({difficulty} level).",
    }
