"""
Pydantic response models for API output structure
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatResponse(BaseModel):
    """Response model for general AI chat"""
    response: str


class BudgetResponse(BaseModel):
    """Response model for budget analysis"""
    summary: Dict[str, Any]  # Contains income, total_expenses, savings_rate, top_expenses
    insights: List[str]


class GoalResponse(BaseModel):
    """Response model for goal planning"""
    plan: Dict[str, Any]  # Contains goal details and required monthly saving
    advice: str


class TaxResponse(BaseModel):
    """Response model for tax advice"""
    tax_advice: str
    estimated_tax: Optional[float] = None
    suggestions: Optional[List[str]] = None


class AnalyticsResponse(BaseModel):
    """Response model for analytics dashboard"""
    trend_data: List[Dict[str, Any]]
    totals: Dict[str, float]


class TransactionResponse(BaseModel):
    """Response model for transaction operations"""
    success: bool
    message: str
    transaction_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    details: Optional[str] = None


class CreateGoalResponse(BaseModel):
    """Response model for creating a goal"""
    success: bool
    message: str
    goal_id: Optional[str] = None


class UpdateGoalResponse(BaseModel):
    """Response model for updating a goal"""
    success: bool
    message: str
    goal_id: Optional[str] = None


class GoalListResponse(BaseModel):
    """Response model for listing goals"""
    goals: List[Dict[str, Any]]
    total: int
