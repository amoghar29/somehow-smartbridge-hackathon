from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.investment import InvestmentType


class InvestmentCreate(BaseModel):
    """Schema for creating an investment"""
    type: InvestmentType
    name: str = Field(..., min_length=2, max_length=100)
    amount_invested: float = Field(..., gt=0)
    current_value: float = Field(..., ge=0)
    purchase_date: datetime
    maturity_date: Optional[datetime] = None
    units: Optional[float] = None
    nav: Optional[float] = None
    interest_rate: Optional[float] = None
    risk_level: str = "moderate"


class InvestmentUpdate(BaseModel):
    """Schema for updating an investment"""
    name: Optional[str] = None
    current_value: Optional[float] = None
    risk_level: Optional[str] = None


class InvestmentResponse(BaseModel):
    """Schema for investment response"""
    id: str
    user_id: str
    type: InvestmentType
    name: str
    amount_invested: float
    current_value: float
    purchase_date: datetime
    returns_percentage: float
    risk_level: str
    
    class Config:
        from_attributes = True


class InvestmentListResponse(BaseModel):
    """Response for a list of investments"""
    investments: List[InvestmentResponse]
    total_invested: float
    total_current_value: float
    overall_returns: float


class InvestmentRecommendation(BaseModel):
    """Schema for a single investment recommendation"""
    type: str
    name: str
    suggested_amount: float
    expected_returns: str
    risk: str
    reasoning: str


class InvestmentRecommendationResponse(BaseModel):
    """Response for AI investment recommendations"""
    risk_profile: str
    recommended_allocation: dict
    specific_recommendations: List[InvestmentRecommendation]
    rebalancing_needed: bool
    rebalancing_suggestions: List[str]
