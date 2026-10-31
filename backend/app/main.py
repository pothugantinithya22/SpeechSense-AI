import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, speech, therapy, xai, visual_guidance, progress, therapist, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="SpeechSense AI Platform API",
    description="Full-stack AI-powered speech sound disorder (SSD) assessment, Explainable AI, and therapy platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(speech.router)
app.include_router(therapy.router)
app.include_router(xai.router)
app.include_router(visual_guidance.router)
app.include_router(progress.router)
app.include_router(therapist.router)
app.include_router(chat.router)

# Direct compatibility aliases for legacy endpoints
@app.post("/api/analyze")
async def analyze_alias(
    audio: UploadFile = File(...),
    target_word: str = Form(...),
    child_id: int = Form(None)
):
    return await speech.analyze_speech(audio, target_word, child_id)

@app.get("/api/health")
def health_alias():
    return speech.health_check()

@app.get("/")
def root():
    return {
        "message": "Welcome to SpeechSense AI API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/speech/health"
    }

if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
