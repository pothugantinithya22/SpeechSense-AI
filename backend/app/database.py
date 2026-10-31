import sqlite3
import hashlib
import json
import os
from datetime import datetime, timedelta
from app.config import DB_PATH

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('child', 'parent', 'therapist')),
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Child profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS child_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        therapist_id INTEGER,
        age INTEGER NOT NULL,
        diagnosis TEXT,
        avatar TEXT DEFAULT 'fox',
        stars INTEGER DEFAULT 0,
        streak_days INTEGER DEFAULT 0,
        last_practice_date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(therapist_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # Practice sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        target_word TEXT NOT NULL,
        transcript TEXT,
        detected_phonemes TEXT,
        expected_phonemes TEXT,
        accuracy REAL NOT NULL,
        per REAL NOT NULL,
        error_count INTEGER DEFAULT 0,
        audio_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(child_id) REFERENCES child_profiles(id) ON DELETE CASCADE
    )
    """)

    # Phoneme breakdown results per session
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phoneme_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        expected_phoneme TEXT NOT NULL,
        detected_phoneme TEXT,
        status TEXT NOT NULL,
        accuracy REAL NOT NULL,
        confidence REAL DEFAULT 0.0,
        FOREIGN KEY(session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE
    )
    """)

    # Personalized therapy plans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS therapy_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        target_phoneme TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        difficulty TEXT DEFAULT 'beginner',
        current_phase INTEGER DEFAULT 1,
        total_phases INTEGER DEFAULT 4,
        exercises_json TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(child_id) REFERENCES child_profiles(id) ON DELETE CASCADE
    )
    """)

    # Clinical therapist notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS therapist_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER NOT NULL,
        therapist_id INTEGER NOT NULL,
        session_id INTEGER,
        note_text TEXT NOT NULL,
        clinical_recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(child_id) REFERENCES child_profiles(id) ON DELETE CASCADE,
        FOREIGN KEY(therapist_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(session_id) REFERENCES practice_sessions(id) ON DELETE SET NULL
    )
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count > 0:
        return

    print("Seeding initial demo data into database...")
    
    # 1. Therapist User
    cursor.execute("""
    INSERT INTO users (username, password_hash, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    """, ("dr_sarah", hash_password("therapist123"), "Dr. Sarah Jenkins, CCC-SLP", "therapist", "sarah.jenkins@speechsense.clinic"))
    therapist_id = cursor.lastrowid

    # 2. Child 1: Leo Miller
    cursor.execute("""
    INSERT INTO users (username, password_hash, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    """, ("child_leo", hash_password("leo123"), "Leo Miller", "child", "parent.miller@example.com"))
    child1_user_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO child_profiles (user_id, therapist_id, age, diagnosis, avatar, stars, streak_days, last_practice_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (child1_user_id, therapist_id, 7, "Speech Sound Disorder - Rhotic /r/ Gliding & Sibilant /s/ Lisp", "fox", 45, 5, datetime.now().strftime("%Y-%m-%d")))
    child1_id = cursor.lastrowid

    # 3. Child 2: Emma Watson
    cursor.execute("""
    INSERT INTO users (username, password_hash, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    """, ("child_emma", hash_password("emma123"), "Emma Watson", "child", "parent.watson@example.com"))
    child2_user_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO child_profiles (user_id, therapist_id, age, diagnosis, avatar, stars, streak_days, last_practice_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (child2_user_id, therapist_id, 6, "Velar Fronting (/k/ -> /t/ substitution)", "bear", 32, 3, datetime.now().strftime("%Y-%m-%d")))
    child2_id = cursor.lastrowid

    # 4. Pre-populate practice sessions for Leo
    now = datetime.now()
    demo_sessions_leo = [
        ("rabbit", ["R", "AE", "B", "AH", "T"], ["W", "AE", "B", "AH", "T"], 80.0, 20.0, 1, (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ("red", ["R", "EH", "D"], ["W", "EH", "D"], 66.7, 33.3, 1, (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
        ("sun", ["S", "AH", "N"], ["TH", "AH", "N"], 66.7, 33.3, 1, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("star", ["S", "T", "AA", "R"], ["S", "T", "AA", "W"], 75.0, 25.0, 1, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        ("rocket", ["R", "AA", "K", "AH", "T"], ["R", "AA", "K", "AH", "T"], 100.0, 0.0, 0, now.strftime("%Y-%m-%d %H:%M:%S"))
    ]

    for word, expected, detected, acc, per, errs, date_str in demo_sessions_leo:
        cursor.execute("""
        INSERT INTO practice_sessions (child_id, target_word, transcript, detected_phonemes, expected_phonemes, accuracy, per, error_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (child1_id, word, f"Child practiced word: {word}", json.dumps(detected), json.dumps(expected), acc, per, errs, date_str))
        sess_id = cursor.lastrowid
        
        # Phoneme breakdown
        for exp, det in zip(expected, detected):
            st = "correct" if exp == det else "substitution"
            acc_val = 100.0 if exp == det else 0.0
            cursor.execute("""
            INSERT INTO phoneme_results (session_id, expected_phoneme, detected_phoneme, status, accuracy, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (sess_id, exp, det, st, acc_val, 0.92 if exp == det else 0.45))

    # 5. Personalized therapy plan for Leo
    leo_r_plan = {
        "phases": [
            {
                "phase": 1,
                "name": "Phase 1: Sound in Isolation",
                "target": "/r/",
                "goal": "Produce clean retroflex or bunched /r/ sound 10 times consecutively.",
                "status": "completed",
                "exercises": [
                    {"type": "cue", "instruction": "Make the 'growling bear' sound: /rrr/", "target": "R", "repetitions": 10},
                    {"type": "mouth_guidance", "instruction": "Tongue blade back, sides of tongue resting against upper molars, lips slightly unrounded.", "target": "R"}
                ]
            },
            {
                "phase": 2,
                "name": "Phase 2: Syllable Construction",
                "target": "/r/ + Vowels",
                "goal": "Master rhotic glide in simple open syllables.",
                "status": "in_progress",
                "exercises": [
                    {"type": "drill", "prompt": "Ray", "target": "R EY", "repetitions": 5},
                    {"type": "drill", "prompt": "Ree", "target": "R IY", "repetitions": 5},
                    {"type": "drill", "prompt": "Row", "target": "R OW", "repetitions": 5}
                ]
            },
            {
                "phase": 3,
                "name": "Phase 3: Word-Initial Positions",
                "target": "Initial /r/ Words",
                "goal": "Transition from syllable to whole word speech with 85% accuracy.",
                "status": "locked",
                "exercises": [
                    {"type": "word", "prompt": "Rabbit", "target": "R AE B AH T"},
                    {"type": "word", "prompt": "Rocket", "target": "R AA K AH T"},
                    {"type": "word", "prompt": "Rainbow", "target": "R EY N B OW"}
                ]
            },
            {
                "phase": 4,
                "name": "Phase 4: Functional Phrases & Sentences",
                "target": "Sentence Fluency",
                "goal": "Generalize correct /r/ articulation into spontaneous conversational speech.",
                "status": "locked",
                "exercises": [
                    {"type": "sentence", "prompt": "The red rabbit ran fast."},
                    {"type": "sentence", "prompt": "Ride the rocket to the stars."}
                ]
            }
        ]
    }

    cursor.execute("""
    INSERT INTO therapy_plans (child_id, target_phoneme, title, description, difficulty, current_phase, total_phases, exercises_json, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (child1_id, "R", "Rhotic /r/ Correction Curriculum", "Targeting persistent /r/ -> /w/ liquid gliding substitution through progressive motor speech feedback.", "intermediate", 2, 4, json.dumps(leo_r_plan), "active"))

    # 6. Therapist clinical note for Leo
    cursor.execute("""
    INSERT INTO therapist_notes (child_id, therapist_id, session_id, note_text, clinical_recommendations)
    VALUES (?, ?, ?, ?, ?)
    """, (child1_id, therapist_id, sess_id, 
          "Leo demonstrated great progress in today's session. /r/ production in 'rocket' showed clean alveolar ridge clearance with no lip-rounding substitution. Transitioning him to Phase 2 syllable and initial-word drills.",
          "Continue daily 10-minute sessions focusing on initial /r/. Use the Visual Articulation tool to remind him of tongue bunched posture before speaking."))

    conn.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    init_db()
