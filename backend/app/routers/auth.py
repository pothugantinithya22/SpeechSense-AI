from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db, hash_password
from app.models.schemas import UserLogin, UserRegister, UserResponse, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=AuthResponse)
def login(creds: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(creds.password)
    
    cursor.execute("""
    SELECT u.id, u.username, u.full_name, u.role, u.email,
           c.id as child_id, c.stars, c.streak_days, c.avatar, c.age, c.diagnosis
    FROM users u
    LEFT JOIN child_profiles c ON u.id = c.user_id
    WHERE u.username = ? AND u.password_hash = ?
    """, (creds.username, pwd_hash))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    user = UserResponse(
        id=row["id"],
        username=row["username"],
        full_name=row["full_name"],
        role=row["role"],
        email=row["email"],
        child_id=row["child_id"],
        stars=row["stars"] or 0,
        streak_days=row["streak_days"] or 0,
        avatar=row["avatar"] or "fox",
        age=row["age"],
        diagnosis=row["diagnosis"]
    )
    
    # Token format for demo session
    token = f"speechsense_token_{user.id}_{user.role}"
    return AuthResponse(token=token, user=user)

@router.post("/register", response_model=AuthResponse)
def register(data: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username is already taken.")

    pwd_hash = hash_password(data.password)
    cursor.execute("""
    INSERT INTO users (username, password_hash, full_name, role, email)
    VALUES (?, ?, ?, ?, ?)
    """, (data.username, pwd_hash, data.full_name, data.role, data.email))
    user_id = cursor.lastrowid

    child_id = None
    if data.role in ("child", "parent"):
        cursor.execute("""
        INSERT INTO child_profiles (user_id, age, diagnosis, avatar, stars, streak_days)
        VALUES (?, ?, ?, 'fox', 0, 1)
        """, (user_id, data.age or 7, data.diagnosis or "Speech Sound Disorder"))
        child_id = cursor.lastrowid

    conn.commit()
    conn.close()

    user = UserResponse(
        id=user_id,
        username=data.username,
        full_name=data.full_name,
        role=data.role,
        email=data.email,
        child_id=child_id,
        stars=0,
        streak_days=1,
        avatar="fox",
        age=data.age,
        diagnosis=data.diagnosis
    )
    token = f"speechsense_token_{user_id}_{data.role}"
    return AuthResponse(token=token, user=user)

@router.get("/demo-users")
def get_demo_users():
    """Provides ready-to-use demo credentials for instant testing."""
    return [
        {
            "username": "child_leo",
            "password": "leo123",
            "role": "child",
            "full_name": "Leo Miller",
            "details": "Child Profile (Age 7, SSD: /r/ and /s/ deficits)"
        },
        {
            "username": "dr_sarah",
            "password": "therapist123",
            "role": "therapist",
            "full_name": "Dr. Sarah Jenkins, CCC-SLP",
            "details": "Clinical Speech-Language Pathologist"
        }
    ]
