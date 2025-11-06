from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from core.auth import get_password_hash, verify_password, create_access_token
from core.database import db
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from core.logger import logger

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(user: UserCreate):
    logger.info(f"Signup attempt for email: {user.email}")
    if db.users.find_one({"email": user.email}):
        logger.warning(f"Signup failed: Email already registered - {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db.users.insert_one({"email": user.email, "password": hashed_password, "name": user.name})
    logger.info(f"User created: {user.email}")
    return {"success": True, "message": "User created"}

@router.post("/login")
def login(user: UserLogin):
    logger.info(f"Login attempt for email: {user.email}")
    db_user = db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        logger.warning(f"Login failed for email: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"Login successful for email: {user.email}")
    return {"access_token": access_token, "token_type": "bearer", "name": db_user.get("name", "User")}
