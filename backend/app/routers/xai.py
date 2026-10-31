from fastapi import APIRouter, Query, Body
from app.services.explainable_ai import generate_xai_explanation

router = APIRouter(prefix="/api/xai", tags=["Explainable AI (XAI)"])

@router.get("/explain")
def explain_error_get(
    expected: str = Query(..., description="Expected target phoneme, e.g. 'R'"),
    detected: str = Query(..., description="Detected produced phoneme, e.g. 'W'")
):
    return generate_xai_explanation(expected, detected)

@router.post("/explain")
def explain_error_post(payload: dict = Body(...)):
    expected = payload.get("expected", "R")
    detected = payload.get("detected", "W")
    confidence = payload.get("confidence", 0.85)
    return generate_xai_explanation(expected, detected, confidence)
