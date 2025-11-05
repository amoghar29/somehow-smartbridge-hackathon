from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from bson import ObjectId


class GoalStatus(str, Enum):
    """Goal status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class GoalType(str, Enum):
    """Goal type based on timeline"""
    SHORT_TERM = "short_term"  # < 1 year
    MEDIUM_TERM = "medium_term"  # 1-3 years
    LONG_TERM = "long_term"  # > 3 years


class SavingStrategy(str, Enum):
    """Saving strategy difficulty"""
    EASY = "easy"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class GoalCategory(str, Enum):
    """Goal categories"""
    EMERGENCY = "emergency"
    EDUCATION = "education"
    TRAVEL = "travel"
    HOME = "home"
    VEHICLE = "vehicle"
    WEDDING = "wedding"
    RETIREMENT = "retirement"
    BUSINESS = "business"
    INVESTMENT = "investment"
    OTHER = "other"


class Milestone(BaseModel):
    """Goal milestone"""
    date: datetime
    amount: float
    percentage: float
    achieved: bool = False
    note: Optional[str] = None


class AIPlan(BaseModel):
    """AI-generated saving plan"""
    recommended_monthly_saving: float
    investment_suggestions: List[Dict] = []
    feasibility_score: float
    risk_assessment: str
    alternative_strategies: List[Dict] = []
    expense_reduction_plan: Dict = {}


class GoalModel(BaseModel):
    """Goal data model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    
    # Goal details
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0
    start_date: datetime
    target_date: datetime
    
    # Classification
    type: GoalType
    status: GoalStatus = GoalStatus.ACTIVE
    category: GoalCategory
    priority: int = 3  # 1-5, 1 being highest
    
    # Savings plan
    saving_strategy: SavingStrategy
    monthly_contribution: float
    contribution_frequency: str = "monthly"
    auto_debit: bool = False
    
    # Progress tracking
    milestones: List[Milestone] = []
    progress_percentage: float = 0
    last_contribution_date: Optional[datetime] = None
    total_contributed: float = 0
    
    # AI Recommendations
    ai_plan: Optional[AIPlan] = None
    
    # Notifications
    reminder_enabled: bool = True
    reminder_day: int = 1  # Day of month for reminder
    last_reminder: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "Europe Vacation",
                "description": "2 weeks trip to Europe",
                "target_amount": 200000,
                "current_amount": 10000,
                "target_date": "2025-06-30",
                "category": "travel",
                "saving_strategy": "moderate",
                "monthly_contribution": 25000
            }
        }