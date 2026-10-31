from fastapi import APIRouter
from app.services.visual_mouth_data import get_phoneme_articulation, PHONEME_ARTICULATION_DATA
from app.services.alignment import CMU_PHONEMES

router = APIRouter(prefix="/api/visual", tags=["Visual Articulation & Mouth Guidance"])

@router.get("/phoneme/{phoneme}")
def get_phoneme_visual(phoneme: str):
    return get_phoneme_articulation(phoneme)

@router.get("/all")
def get_all_phonemes():
    result = []
    for ph in CMU_PHONEMES:
        art = get_phoneme_articulation(ph)
        result.append({
            "phoneme": ph,
            "label": f"/{ph}/",
            "manner": art.get("manner", "Oral Sound"),
            "place": art.get("place", "Oral Cavity"),
            "voicing": art.get("voicing", "Voiced"),
            "has_custom_model": ph in PHONEME_ARTICULATION_DATA
        })
    return result
