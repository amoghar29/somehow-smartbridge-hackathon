"""
Database models for MongoDB collections
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class TransactionDB(BaseModel):
    """Transaction database model"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    description: str
    amount: float
    category: str
    type: str  # "income" or "expense"
    date: str  # ISO format date string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatMessageDB(BaseModel):
    """Chat message database model"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    question: str
    response: str
    persona: str = "professional"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class GoalDB(BaseModel):
    """Financial goal database model"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    target_amount: float
    current_amount: float = 0.0
    category: str
    deadline: str  # ISO format date string
    monthly_required: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # "active", "completed", "paused"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
