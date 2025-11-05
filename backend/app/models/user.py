from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, List
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class UserProfile(BaseModel):
    """User profile information"""
    age: Optional[int] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    risk_profile: str = "moderate"  # conservative, moderate, aggressive
    financial_goals: List[str] = []


class UserPreferences(BaseModel):
    """User preferences"""
    currency: str = "INR"
    notification_enabled: bool = True
    email_alerts: bool = True
    savings_reminder: bool = True
    theme: str = "light"  # light, dark


class FinancialSummary(BaseModel):
    """User's financial summary"""
    total_income: float = 0
    total_expenses: float = 0
    total_savings: float = 0
    total_investments: float = 0
    net_worth: float = 0
    monthly_avg_income: float = 0
    monthly_avg_expenses: float = 0
    savings_rate: float = 0


class UserModel(BaseModel):
    """User data model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    full_name: str
    phone_number: Optional[str] = None
    
    # Profile
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    financial_summary: FinancialSummary = Field(default_factory=FinancialSummary)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    email_verified: bool = False
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "phone_number": "+919876543210",
                "profile": {
                    "age": 30,
                    "occupation": "Software Engineer",
                    "annual_income": 1200000,
                    "risk_profile": "moderate",
                    "financial_goals": ["retirement", "home", "education"]
                }
            }
        }