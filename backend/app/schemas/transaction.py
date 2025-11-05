from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from app.models.transaction import (
    TransactionType,
    TransactionCategory,
    PaymentMethod
)


class TransactionCreate(BaseModel):
    """Schema for creating a transaction"""
    type: TransactionType
    category: TransactionCategory
    amount: float = Field(..., gt=0, description="Amount must be positive")
    description: str = Field(..., min_length=1, max_length=500)
    date: datetime = Field(default_factory=datetime.utcnow)
    payment_method: Optional[PaymentMethod] = None
    tags: List[str] = []
    notes: Optional[str] = None
    recurring: bool = False
    recurring_frequency: Optional[str] = None
    
    @validator('recurring_frequency')
    def validate_recurring_frequency(cls, v, values):
        if values.get('recurring') and not v:
            raise ValueError('recurring_frequency is required when recurring is True')
        if v and v not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise ValueError('Invalid recurring_frequency')
        return v


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction"""
    category: Optional[TransactionCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: str
    user_id: str
    type: TransactionType
    category: TransactionCategory
    amount: float
    description: str
    date: datetime
    payment_method: Optional[PaymentMethod]
    tags: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    """Schema for transaction list response"""
    transactions: List[TransactionResponse]
    total: int
    limit: int
    offset: int


class TransactionAnalytics(BaseModel):
    """Schema for transaction analytics"""
    period: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    category_breakdown: dict
    monthly_trend: List[dict]
    anomalies: List[dict]


class EmailParseRequest(BaseModel):
    """Schema for email parsing request"""
    email_content: str = Field(..., min_length=10)
    email_subject: Optional[str] = None