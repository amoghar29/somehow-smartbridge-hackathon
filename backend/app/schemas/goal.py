from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict
from app.models.goal import (
    GoalStatus,
    GoalType,
    SavingStrategy,
    GoalCategory
)


class GoalPlanRequest(BaseModel):
    """Request schema for creating a goal plan"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: datetime
    category: GoalCategory
    
    @validator('target_date')
    def validate_target_date(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Target date must be in the future')
        return v
    
    @validator('current_amount')
    def validate_current_amount(cls, v, values):
        if 'target_amount' in values and v > values['target_amount']:
            raise ValueError('Current amount cannot exceed target amount')
        return v


class GoalCreate(BaseModel):
    """Schema for creating a goal"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: datetime
    category: GoalCategory
    saving_strategy: SavingStrategy
    monthly_contribution: float = Field(..., gt=0)
    priority: int = Field(default=3, ge=1, le=5)
    auto_debit: bool = False


class GoalUpdate(BaseModel):
    """Schema for updating a goal"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    monthly_contribution: Optional[float] = Field(None, gt=0)
    priority: Optional[int] = Field(None, ge=1, le=5)
    auto_debit: Optional[bool] = None


class GoalContribution(BaseModel):
    """Schema for adding contribution to goal"""
    amount: float = Field(..., gt=0)
    note: Optional[str] = None


class GoalResponse(BaseModel):
    """Schema for goal response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    target_amount: float
    current_amount: float
    progress_percentage: float
    target_date: datetime
    status: GoalStatus
    category: GoalCategory
    saving_strategy: SavingStrategy
    monthly_contribution: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class StrategyBreakdown(BaseModel):
    """Individual strategy breakdown"""
    monthly_saving: float
    time_to_goal: float
    feasibility: str
    lifestyle_impact: str
    breakdown: Dict[str, float]
    additional_income_needed: float = 0


class GoalPlanResponse(BaseModel):
    """Response schema for goal planning"""
    goal_details: Dict
    financial_analysis: Dict
    strategies: Dict[str, StrategyBreakdown]
    ai_recommendations: Dict


class GoalProgressResponse(BaseModel):
    """Response schema for goal progress"""
    goal: GoalResponse
    progress: Dict
    milestones: List[Dict]
    visualization_data: Dict
    on_track: bool
    projected_completion: Optional[datetime]


class GoalListResponse(BaseModel):
    """Response schema for goal list"""
    goals: List[GoalResponse]
    total: int
    active_count: int
    completed_count: int