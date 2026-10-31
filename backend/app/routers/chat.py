import os
from fastapi import APIRouter, Body
from app.config import GEMINI_API_KEY

router = APIRouter(prefix="/api/chat", tags=["Speech Therapy Assistant Chatbot"])

CLINICAL_KNOWLEDGE = {
    "r": "For the /r/ sound (rhotic), remind the child to keep their tongue blade pulled back toward the palate without letting their lips round into a /w/.",
    "s": "For the /s/ sound, check that the tongue tip stays behind the top teeth fence and isn't poking between the incisors (frontal lisp).",
    "th": "For the /th/ sound, the tongue gently rests between the teeth with soft continuous air release.",
    "k": "For the /k/ sound, have the child keep their tongue tip flat against the bottom of their mouth while popping the back of their tongue against the soft palate.",
    "l": "For the /l/ sound, the tongue tip taps firmly behind the top front teeth, letting air flow out the sides.",
    "plan": "Personalized therapy plans break remediation down into 4 phases: Sound in Isolation, Syllables, Target Words, and Conversational Sentences.",
    "xai": "Explainable AI in SpeechSense clarifies the acoustic and articulatory reasons why a phoneme was flagged, comparing formant shifts and articulatory positioning.",
    "visual": "The Visual Articulation tool provides an interactive SVG cross-section of the vocal tract showing exact tongue and lip placement."
}

def generate_slp_response(question: str) -> str:
    q = question.lower()
    for key, ans in CLINICAL_KNOWLEDGE.items():
        if key in q:
            return f"**SpeechSense SLP Clinical Assistant**: {ans}"
            
    if any(greet in q for greet in ["hello", "hi", "hey"]):
        return "Hello! I am your SpeechSense clinical assistant. I can explain phoneme articulation, guide practice drills, or interpret child assessment scores. How can I help today?"
        
    return (
        "I can provide evidence-based speech therapy guidance for sounds like /r/, /s/, /k/, /l/, /th/, "
        "explain how our HuBERT AI analyzes pronunciation, or help you understand the child's therapy plan."
    )

@router.post("")
def chat_endpoint(payload: dict = Body(...)):
    prompt = payload.get("message", payload.get("prompt", "")).strip()
    if not prompt:
        return {"response": "Please enter a message or question."}

    # If Gemini API key configured, attempt external call, else fallback to SLP expert system
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(
                f"You are SpeechSense AI, an expert pediatric speech-language pathologist assistant. Answer concisely and kindly: {prompt}"
            )
            return {"response": resp.text}
        except Exception:
            pass

    return {"response": generate_slp_response(prompt)}
