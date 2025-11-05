from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from bson import ObjectId


class TransactionType(str, Enum):
    """Transaction types"""
    INCOME = "income"
    EXPENSE = "expense"
    INVESTMENT = "investment"
    SAVINGS = "savings"


class TransactionCategory(str, Enum):
    """Transaction categories"""
    # Income
    SALARY = "salary"
    BUSINESS = "business"
    FREELANCE = "freelance"
    INVESTMENT_INCOME = "investment_income"
    OTHER_INCOME = "other_income"
    
    # Expenses
    FOOD = "food"
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RENT = "rent"
    EMI = "emi"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    SAVINGS_DEPOSIT = "savings_deposit"
    OTHER = "other"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    OTHER = "other"


class TransactionSource(str, Enum):
    """Transaction source"""
    MANUAL = "manual"
    EMAIL = "email"
    BANK_SYNC = "bank_sync"
    RECURRING = "recurring"


class TransactionModel(BaseModel):
    """Transaction data model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    
    # Transaction details
    type: TransactionType
    category: TransactionCategory
    amount: float
    description: str
    date: datetime
    
    # Optional fields
    payment_method: Optional[PaymentMethod] = None
    tags: List[str] = []
    notes: Optional[str] = None
    
    # Recurring transactions
    recurring: bool = False
    recurring_frequency: Optional[str] = None  # daily, weekly, monthly, yearly
    recurring_end_date: Optional[datetime] = None
    parent_transaction_id: Optional[str] = None  # For recurring transactions
    
    # Source tracking
    source: TransactionSource = TransactionSource.MANUAL
    email_id: Optional[str] = None
    
    # AI Analysis
    ai_insights: Optional[Dict] = None
    anomaly_flag: bool = False
    confidence_score: Optional[float] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "type": "expense",
                "category": "food",
                "amount": 1500,
                "description": "Restaurant dinner",
                "date": "2024-11-15T19:30:00Z",
                "payment_method": "card",
                "tags": ["dining", "weekend"]
            }
        }