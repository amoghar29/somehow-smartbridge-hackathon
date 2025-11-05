from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from bson import ObjectId


class ChatRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatContext(str, Enum):
    """Chat context types"""
    GENERAL = "general"
    GOAL_PLANNING = "goal_planning"
    TAX_ADVICE = "tax_advice"
    INVESTMENT = "investment"
    LEARNING = "learning"
    SPENDING_ANALYSIS = "spending_analysis"


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: ChatRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = None


class RetrievedDocument(BaseModel):
    """Retrieved document from RAG"""
    content: str
    source: str
    relevance_score: float


class ChatSession(BaseModel):
    """Chat session model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    session_id: str  # Unique session identifier
    context: ChatContext = ChatContext.GENERAL
    
    # Messages
    messages: List[ChatMessage] = []
    
    # RAG Context
    retrieved_documents: List[Dict] = []
    embeddings_used: List[str] = []
    
    # Session Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Analytics
    message_count: int = 0
    user_satisfaction: Optional[int] = None  # 1-5 rating
    feedback: Optional[str] = None
    tags: List[str] = []
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "sess_abc123",
                "context": "general",
                "messages": [
                    {
                        "role": "user",
                        "content": "How can I save more money?",
                        "timestamp": "2024-11-15T10:30:00Z"
                    }
                ]
            }
        }