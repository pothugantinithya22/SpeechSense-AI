from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Authentication
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "child" # child, parent, therapist
    email: Optional[str] = None
    age: Optional[int] = 7
    diagnosis: Optional[str] = "Speech Sound Disorder"

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    email: Optional[str] = None
    child_id: Optional[int] = None
    stars: Optional[int] = 0
    streak_days: Optional[int] = 0
    avatar: Optional[str] = "fox"
    age: Optional[int] = None
    diagnosis: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

# Speech Analysis & Phoneme Assessment
class AlignmentItem(BaseModel):
    expected: str
    detected: str
    status: str # correct, substitution, omission, insertion

class PhonemeErrorItem(BaseModel):
    word: str
    phoneme: str
    type: str # substitution, omission, insertion
    produced: str
    expected: str
    detected: Optional[str] = None
    accuracy: float
    confidence: Optional[float] = 0.0
    tip_title: Optional[str] = None
    tip: Optional[str] = None
    xai_explanation: Optional[str] = None

class PhonemeDetailItem(BaseModel):
    ph: str
    acc: float
    err: str
    words: str
    confidence: Optional[float] = 0.0

class SpeechAnalysisResponse(BaseModel):
    target_word: str
    expected_phonemes: List[str]
    detected_phonemes: List[str]
    alignment: List[AlignmentItem]
    phoneme_errors: List[PhonemeErrorItem]
    feedback: List[Dict[str, Any]]
    all_phonemes: List[PhonemeDetailItem]
    accuracy: float
    per: float
    summary: Dict[str, str]
    recommendations: List[str]
    xai_diagnostics: Optional[Dict[str, Any]] = None

# Personalized Therapy
class TherapyExercise(BaseModel):
    type: str
    prompt: Optional[str] = None
    instruction: Optional[str] = None
    target: Optional[str] = None
    repetitions: Optional[int] = 5

class TherapyPhase(BaseModel):
    phase: int
    name: str
    target: str
    goal: str
    status: str # completed, in_progress, locked
    exercises: List[Dict[str, Any]]

class TherapyPlanResponse(BaseModel):
    id: int
    child_id: int
    target_phoneme: str
    title: str
    description: Optional[str] = None
    difficulty: str
    current_phase: int
    total_phases: int
    phases: List[TherapyPhase]
    status: str
    created_at: str

class TherapyGenerateRequest(BaseModel):
    child_id: int
    target_phoneme: str
    difficulty: Optional[str] = "beginner"

# Therapist Notes & Clinical Insights
class TherapistNoteCreate(BaseModel):
    child_id: int
    session_id: Optional[int] = None
    note_text: str
    clinical_recommendations: Optional[str] = None

class TherapistNoteResponse(BaseModel):
    id: int
    child_id: int
    therapist_id: int
    therapist_name: str
    session_id: Optional[int] = None
    note_text: str
    clinical_recommendations: Optional[str] = None
    created_at: str

# Progress Analytics
class ProgressSummary(BaseModel):
    child_id: int
    child_name: str
    avatar: str
    stars: int
    streak_days: int
    total_sessions: int
    average_accuracy: float
    average_per: float
    phoneme_mastery: Dict[str, float]
    recent_sessions: List[Dict[str, Any]]
    error_distribution: Dict[str, int]
