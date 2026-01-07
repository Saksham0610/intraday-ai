from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import SessionLocal
from .models import User

# Use Argon2 (modern, no 72-byte limit, Python 3.13 safe)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_email = request.cookies.get("user")

    if not user_email:
        raise HTTPException(status_code=401, detail="Not logged in")

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user
