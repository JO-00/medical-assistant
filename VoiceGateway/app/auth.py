import jwt
import time
import bcrypt
import asyncpg
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from config import JWT_SECRET, ALGORITHM, DB_DSN
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()
ACTIVE_SESSIONS = {}

# Database connection pool
db_pool = None

async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=10)
    return db_pool

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    confirm_password: str
    qualification: str
    specialty: str = None
    license_number: str = None
    years_of_experience: int = None
    clinic_name: str = None
    phone_number: str = None
    languages_spoken: list = []
    timezone: str = None
    bio: str = None

class AuthResponse(BaseModel):
    token: str
    user: dict

@router.post("/auth/login")
async def login(data: LoginRequest):
    """Login with email and password"""
    time.sleep(0.5)  # Prevent brute force
    
    pool = await get_db_pool()
    
    # Query doctor by email
    query = """
        SELECT id_medecin, nom, prenom, email, password, 
               specialite, qualification, phone_number
        FROM public.medecin 
        WHERE email = $1
    """
    doctor = await pool.fetchrow(query, data.email.lower())
    
    if not doctor:
        logger.warning(f"Login attempt with unknown email: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    stored_password = doctor['password']
    if not stored_password or not stored_password.startswith('$2b$'):
        # Legacy or unhashed password - handle gracefully
        if stored_password != data.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    else:
        # Check hashed password
        if not bcrypt.checkpw(data.password.encode('utf-8'), stored_password.encode('utf-8')):
            logger.warning(f"Failed login attempt for: {data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create user dict for session
    user = {
        "id": doctor['id_medecin'],
        "email": doctor['email'],
        "name": f"{doctor['prenom']} {doctor['nom']}".strip() or doctor['nom'] or doctor['email'],
        "first_name": doctor['prenom'],
        "last_name": doctor['nom'],
        "qualification": doctor.get('qualification'),
        "specialty": doctor.get('specialite'),
        "phone": doctor.get('phone_number')
    }
    
    # Generate JWT token
    token = jwt.encode(
        {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        JWT_SECRET,
        algorithm=ALGORITHM
    )
    
    # Store session
    ACTIVE_SESSIONS[token] = user
    
    logger.info(f"User logged in: {user['email']} (ID: {user['id']})")
    return {"token": token, "user": user}

@router.post("/auth/signup")
async def signup(data: SignupRequest):
    """Register a new doctor"""
    # Validate
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")
    
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    pool = await get_db_pool()
    
    # Check if email already exists
    existing = await pool.fetchrow(
        "SELECT email FROM public.medecin WHERE email = $1",
        data.email.lower()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), salt).decode('utf-8')
    
    # Parse name
    name_parts = data.full_name.strip().split()
    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    # Insert new doctor
    query = """
        INSERT INTO public.medecin (
            email,
            password,
            nom,
            prenom,
            etat,
            date_debut_convention,
            date_creation,
            date_last_maj,
            specialite,
            qualification,
            phone_number,
            presentation,
            flag_inscri_portail
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        )
        RETURNING id_medecin, email, nom, prenom
    """
    
    now = datetime.utcnow()
    
    try:
        result = await pool.fetchrow(
            query,
            data.email.lower(),
            hashed_password,
            last_name or "Unknown",
            first_name or "Doctor",
            1,  # etat = active
            now,  # date_debut_convention
            now,  # date_creation
            now,  # date_last_maj
            data.specialty or "General Practice",
            data.qualification,
            data.phone_number,
            data.bio or "",
            True  # flag_inscri_portail
        )
        
        # Also store additional info in a doctor_profile table if needed
        # For now, we'll use the medecin table columns we have
        
        user = {
            "id": result['id_medecin'],
            "email": result['email'],
            "name": f"{result['prenom']} {result['nom']}".strip(),
            "first_name": result['prenom'],
            "last_name": result['nom'],
        }
        
        # Generate token automatically after signup
        token = jwt.encode(
            {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "exp": datetime.utcnow() + timedelta(days=7)
            },
            JWT_SECRET,
            algorithm=ALGORITHM
        )
        
        ACTIVE_SESSIONS[token] = user
        
        logger.info(f"New doctor registered: {user['email']} (ID: {user['id']})")
        
        return {
            "message": "Account created successfully",
            "token": token,
            "user": user
        }
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create account")

def get_current_user(authorization: str = Header(None)):
    """Get current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header provided")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # First check active sessions
    user = ACTIVE_SESSIONS.get(token)
    if user:
        return user
    
    # If not in sessions, verify JWT
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # You could also verify the user still exists in DB here
        return {
            "id": payload["id"],
            "email": payload["email"],
            "name": payload["name"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")