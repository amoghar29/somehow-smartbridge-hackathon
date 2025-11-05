from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta

from app.config.database import get_database
from app.config.settings import settings
from app.schemas.auth import UserRegister, Token, PasswordChange
from app.models.user import UserModel
from app.utils.security import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user
    
    - **email**: User's email address
    - **username**: Unique username (alphanumeric)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **full_name**: User's full name
    """
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    user = UserModel(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number
    )
    
    # Insert into database
    result = await db.users.insert_one(user.model_dump(by_alias=True))
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login and get access token
    
    - **username**: Email or username
    - **password**: User's password
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["_id"], "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Change user password
    
    - **old_password**: Current password
    - **new_password**: New password (min 8 chars, uppercase, digit)
    """
    from app.utils.security import verify_password
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Update password
    new_password_hash = get_password_hash(password_data.new_password)
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    # Remove sensitive data
    user_info = {
        "id": current_user["_id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "profile": current_user.get("profile", {}),
        "preferences": current_user.get("preferences", {}),
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login")
    }
    
    return user_info