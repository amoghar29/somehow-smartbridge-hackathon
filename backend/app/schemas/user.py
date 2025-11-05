from pydantic import BaseModel, Field
from typing import Optional, List


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    age: Optional[int] = Field(None, ge=18, le=100)
    occupation: Optional[str] = None
    annual_income: Optional[float] = Field(None, gt=0)
    risk_profile: Optional[str] = None
    financial_goals: Optional[List[str]] = None


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""
    currency: Optional[str] = None
    notification_enabled: Optional[bool] = None
    email_alerts: Optional[bool] = None
    savings_reminder: Optional[bool] = None
    theme: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user details"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile: Optional[UserProfileUpdate] = None
    preferences: Optional[UserPreferencesUpdate] = None
