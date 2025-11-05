from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.config.database import get_database
from app.utils.security import get_current_user
from app.models.investment import InvestmentModel
from app.schemas.investment import (
    InvestmentCreate,
    InvestmentResponse,
    InvestmentListResponse,
    InvestmentRecommendationResponse
)

router = APIRouter(prefix="/api/v1/investments", tags=["Investments"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_investment(
    investment: InvestmentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a new investment"""
    investment_model = InvestmentModel(
        user_id=current_user["_id"],
        **investment.model_dump()
    )
    
    result = await db.investments.insert_one(
        investment_model.model_dump(by_alias=True)
    )
    
    return {"id": str(result.inserted_id), "message": "Investment added successfully"}


@router.get("/", response_model=InvestmentListResponse)
async def get_investments(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all investments for the current user"""
    investments = await db.investments.find({"user_id": current_user["_id"]}).to_list(None)
    
    total_invested = sum(inv["amount_invested"] for inv in investments)
    total_current_value = sum(inv.get("current_value", inv["amount_invested"]) for inv in investments)
    
    overall_returns = 0
    if total_invested > 0:
        overall_returns = ((total_current_value - total_invested) / total_invested) * 100
    
    investment_responses = [
        InvestmentResponse(
            id=str(inv["_id"]),
            user_id=inv["user_id"],
            type=inv["type"],
            name=inv["name"],
            amount_invested=inv["amount_invested"],
            current_value=inv.get("current_value", inv["amount_invested"]),
            purchase_date=inv["purchase_date"],
            returns_percentage=inv.get("returns_percentage", 0),
            risk_level=inv.get("risk_level", "moderate")
        )
        for inv in investments
    ]
    
    return InvestmentListResponse(
        investments=investment_responses,
        total_invested=total_invested,
        total_current_value=total_current_value,
        overall_returns=overall_returns
    )


@router.get("/recommendations", response_model=InvestmentRecommendationResponse)
async def get_investment_recommendations(
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered investment recommendations"""
    # This is a placeholder. In a real application, this would involve a more
    # sophisticated service that analyzes user's risk profile, goals, and market data.
    risk_profile = current_user.get("profile", {}).get("risk_profile", "moderate")
    
    if risk_profile == "aggressive":
        allocation = {"equity": 70, "debt": 20, "gold": 5, "crypto": 5}
    elif risk_profile == "moderate":
        allocation = {"equity": 50, "debt": 30, "gold": 15, "crypto": 5}
    else: # conservative
        allocation = {"equity": 30, "debt": 50, "gold": 20, "crypto": 0}
        
    recommendations = [
        {
            "type": "mutual_funds",
            "name": "Nifty 50 Index Fund",
            "suggested_amount": 5000,
            "expected_returns": "10-12%",
            "risk": "moderate",
            "reasoning": "Broad market exposure and low cost."
        },
        {
            "type": "ppf",
            "name": "Public Provident Fund",
            "suggested_amount": 10000,
            "expected_returns": "7.1%",
            "risk": "low",
            "reasoning": "Tax-free returns and government backed."
        }
    ]
    
    return InvestmentRecommendationResponse(
        risk_profile=risk_profile,
        recommended_allocation=allocation,
        specific_recommendations=recommendations,
        rebalancing_needed=False,
        rebalancing_suggestions=[]
    )
