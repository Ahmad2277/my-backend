import hashlib
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import User

# ─────────────────────────────────────────
# JWT Token setup
# ─────────────────────────────────────────
SECRET_KEY = "renovision_secret_key_2024_lgu"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ─────────────────────────────────────────
# Hash password using sha256 + bcrypt
# Same method used in BOTH register and login
# ─────────────────────────────────────────
def hash_password(password: str):
    # Step 1 — convert password to sha256
    hashed_input = hashlib.sha256(
        password.encode()
    ).digest()
    # Step 2 — bcrypt the sha256 hash
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(hashed_input, salt)


# ─────────────────────────────────────────
# Verify password — MUST match hash_password
# ─────────────────────────────────────────
def verify_password(plain_password: str,
                    stored_hash):
    # Step 1 — convert password to sha256
    hashed_input = hashlib.sha256(
        plain_password.encode()
    ).digest()

    # Handle both bytes and string stored hash
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')

    # Step 2 — verify against stored bcrypt hash
    try:
        return bcrypt.checkpw(
            hashed_input, stored_hash
        )
    except Exception as e:
        print(f"Password verify error: {e}")
        return False


# ─────────────────────────────────────────
# Create JWT access token
# ─────────────────────────────────────────
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        hours=TOKEN_EXPIRE_HOURS
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token


# ─────────────────────────────────────────
# Verify JWT token
# ─────────────────────────────────────────
def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


# ─────────────────────────────────────────
# Register new user
# ─────────────────────────────────────────
def register_user(db: Session, name: str,
                  email: str, password: str):
    # Check if email already exists
    existing = db.query(User).filter(
        User.email == email
    ).first()

    if existing:
        return {
            "success": False,
            "error": "Email already registered"
        }

    # Hash password and save user
    hashed = hash_password(password)

    # Convert bytes to string for database storage
    if isinstance(hashed, bytes):
        hashed = hashed.decode('utf-8')

    user = User(
        name=name,
        email=email,
        password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token
    token = create_token({"sub": user.email})

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# ─────────────────────────────────────────
# Login existing user
# ─────────────────────────────────────────
def login_user(db: Session, email: str,
               password: str):
    # Find user by email
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return {
            "success": False,
            "error": "Email not found. Please register first."
        }

    # Verify password
    password_correct = verify_password(
        password, user.password
    )

    if not password_correct:
        return {
            "success": False,
            "error": "Incorrect password. Please try again."
        }

    # Create token
    token = create_token({"sub": user.email})

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# ─────────────────────────────────────────
# Get all users (admin view)
# ─────────────────────────────────────────
def get_all_users(db: Session):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "created_at": str(u.created_at)
        }
        for u in users
    ]
# ─────────────────────────────────────────
# Google OAuth Login
# Creates user if not exists
# ─────────────────────────────────────────
def google_login(db: Session, name: str,
                 email: str, google_uid: str):
    # Check if user exists
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        # Create new user from Google
        user = User(
            name=name,
            email=email,
            password=f"google_{google_uid}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create token
    token = create_token({"sub": user.email})

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }
