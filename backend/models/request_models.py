"""
Pydantic request models for API input validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional


class ChatRequest(BaseModel):
    """Request model for general AI chat"""
    question: str = Field(..., min_length=1, description="User's question")
    persona: str = Field(default="general", description="User persona (student/professional/general)")

    @validator('question')
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()


class BudgetRequest(BaseModel):
    """Request model for budget analysis"""
    income: float = Field(..., gt=0, description="Monthly income")
    expenses: Dict[str, float] = Field(..., description="Expense categories with amounts")
    persona: str = Field(default="general", description="User persona")

    @validator('expenses')
    def validate_expenses(cls, v):
        for category, amount in v.items():
            if amount < 0:
                raise ValueError(f'Expense amount for {category} cannot be negative')
        return v


class GoalRequest(BaseModel):
    """Request model for goal planning"""
    goal_name: str = Field(..., min_length=1, description="Name of the financial goal")
    target_amount: float = Field(..., gt=0, description="Target amount to save")
    months: int = Field(..., gt=0, description="Time period in months")
    income: float = Field(..., gt=0, description="Monthly income")
    persona: str = Field(default="general", description="User persona")
    current_savings: Optional[float] = Field(default=0.0, ge=0, description="Current savings")

    @validator('goal_name')
    def goal_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Goal name cannot be empty')
        return v.strip()


class TransactionRequest(BaseModel):
    """Request model for adding transactions"""
    description: str = Field(..., min_length=1, description="Transaction description")
    amount: float = Field(..., gt=0, description="Transaction amount")
    category: str = Field(..., min_length=1, description="Transaction category")
    type: str = Field(..., description="Transaction type (income/expense)")

    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['income', 'expense']
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of {allowed_types}')
        return v.lower()

    @validator('description')
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

    @validator('category')
    def category_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()


class TaxRequest(BaseModel):
    """Request model for tax advice"""
    income: float = Field(..., gt=0, description="Annual income")
    persona: str = Field(default="general", description="User persona")
    deductions: Optional[Dict[str, float]] = Field(default=None, description="Current deductions")


class CreateGoalRequest(BaseModel):
    """Request model for creating a goal in database"""
    name: str = Field(..., min_length=1, description="Goal name")
    target_amount: float = Field(..., gt=0, description="Target amount to achieve")
    current_amount: float = Field(default=0.0, ge=0, description="Current saved amount")
    category: str = Field(..., min_length=1, description="Goal category (Emergency Fund, Travel, Car, Home, etc.)")
    deadline: str = Field(..., description="Goal deadline in ISO format")
    monthly_required: Optional[float] = Field(default=None, ge=0, description="Required monthly savings")

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Goal name cannot be empty')
        return v.strip()

    @validator('category')
    def category_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()


class UpdateGoalRequest(BaseModel):
    """Request model for updating a goal"""
    current_amount: Optional[float] = Field(default=None, ge=0, description="Updated current amount")
    status: Optional[str] = Field(default=None, description="Goal status (active/paused/completed)")
    monthly_required: Optional[float] = Field(default=None, ge=0, description="Updated monthly requirement")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'paused', 'completed']
            if v.lower() not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
            return v.lower()
        return v
