from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from bson import ObjectId


class InvestmentType(str, Enum):
    """Investment types"""
    STOCKS = "stocks"
    MUTUAL_FUNDS = "mutual_funds"
    FIXED_DEPOSIT = "fixed_deposit"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    BONDS = "bonds"
    PPF = "ppf"
    NPS = "nps"
    OTHER = "other"


class InvestmentModel(BaseModel):
    """Investment data model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    
    # Investment details
    type: InvestmentType
    name: str
    amount_invested: float
    current_value: float
    purchase_date: datetime
    
    # Optional fields
    maturity_date: Optional[datetime] = None
    returns_percentage: float = 0
    
    # Specific details
    units: Optional[float] = None
    nav: Optional[float] = None  # For mutual funds
    interest_rate: Optional[float] = None  # For FD, bonds
    
    # Tracking
    performance_history: List[Dict] = []  # [{date, value, returns}]
    dividends_received: float = 0
    
    # Risk & Tax
    risk_level: str = "moderate"  # low, moderate, high
    liquidity: str = "medium"  # high, medium, low
    tax_category: str = "other"  # equity, debt, etc.
    lock_in_period: Optional[int] = None  # in months
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "type": "mutual_funds",
                "name": "Axis Bluechip Fund",
                "amount_invested": 100000,
                "current_value": 115000,
                "purchase_date": "2024-01-15T10:00:00Z",
                "units": 2500,
                "nav": 46
            }
        }
