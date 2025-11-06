"""
Finance-related API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import json
from pathlib import Path

from models.request_models import (
    ChatRequest,
    BudgetRequest,
    GoalRequest,
    TransactionRequest,
    TaxRequest
)
from models.response_models import (
    ChatResponse,
    BudgetResponse,
    GoalResponse,
    TransactionResponse,
    AnalyticsResponse,
    TaxResponse,
    ErrorResponse
)
from agents.budget_agent import analyze_budget
from agents.goal_agent import plan_goal
from agents.tax_agent import get_tax_advice
from agents.intent_router import route_intent, get_fallback_response
from core.granite_api import generate
from core.logger import logger
from config.settings import DATA_DIR
from core.database import db
from jose import JWTError, jwt
from config.settings import SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

@router.post("/ai/generate", response_model=ChatResponse)
async def generate_ai_response(request: ChatRequest, user=Depends(get_current_user)):
    logger.info(f"AI generate request from user: {user.get('email', 'unknown')} | Question: {request.question}")
    """
    General AI response endpoint - Always uses AI model for all questions

    Args:
        request: ChatRequest with question and persona

    Returns:
        ChatResponse: AI-generated response
    """
    try:
        logger.info(f"AI generate request: {request.question[:50]}...")

        # Create a well-structured prompt for better responses
        prompt = f"""You are a professional financial advisor. Answer the following question with practical and accurate advice.

Question: {request.question}

Answer:"""

        response_text = generate(prompt, max_new_tokens=150, temperature=0.7)

        # Save conversation to MongoDB
        db.conversations.insert_one({
            "user_id": str(user["_id"]),
            "question": request.question,
            "response": response_text,
            "timestamp": datetime.utcnow()
        })
        logger.info(f"AI response saved for user: {user.get('email', 'unknown')}")

        # If response is too short or nonsensical, provide a fallback
        if not response_text or len(response_text.strip()) < 20:
            response_text = """I'm here to help with your financial questions! I can assist with:

        - Budget planning and expense tracking
        - Savings goals and strategies
        - Investment basics and portfolio allocation
        - Tax planning and deductions
        - Debt management

        Please ask a specific question and I'll provide detailed advice."""

        return ChatResponse(response=response_text)

    except Exception as e:
        logger.error(f"AI generate failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/budget-summary", response_model=BudgetResponse)
async def get_budget_summary(request: BudgetRequest, user=Depends(get_current_user)):
    logger.info(f"Budget analysis request from user: {user.get('email', 'unknown')} | Income: {request.income}")
    """
    Budget analysis endpoint

    Args:
        request: BudgetRequest with income, expenses, and persona

    Returns:
        BudgetResponse: Budget summary and insights
    """
    try:
        logger.info(f"Budget analysis request for income: {request.income}")

        result = analyze_budget(
            income=request.income,
            expenses=request.expenses,
            persona=request.persona
        )

        return BudgetResponse(
            summary=result["summary"],
            insights=result["insights"]
        )

    except Exception as e:
        logger.error(f"Budget analysis failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/goal-planner", response_model=GoalResponse)
async def plan_financial_goal(request: GoalRequest, user=Depends(get_current_user)):
    logger.info(f"Goal planning request from user: {user.get('email', 'unknown')} | Goal: {request.goal_name}")
    """
    Goal planning endpoint

    Args:
        request: GoalRequest with goal details

    Returns:
        GoalResponse: Savings plan and advice
    """
    try:
        logger.info(f"Goal planning request: {request.goal_name}")

        result = plan_goal(
            goal_name=request.goal_name,
            target_amount=request.target_amount,
            months=request.months,
            income=request.income,
            persona=request.persona,
            current_savings=request.current_savings
        )

        return GoalResponse(
            plan=result["plan"],
            advice=result["advice"]
        )

    except Exception as e:
        logger.error(f"Goal planning failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/tax-advice", response_model=TaxResponse)
async def get_tax_advisory(request: TaxRequest, user=Depends(get_current_user)):
    logger.info(f"Tax advice request from user: {user.get('email', 'unknown')} | Income: {request.income}")
    """
    Tax advice endpoint

    Args:
        request: TaxRequest with income and persona

    Returns:
        TaxResponse: Tax-saving advice
    """
    try:
        logger.info(f"Tax advice request for income: {request.income}")

        advice = get_tax_advice(
            income=request.income,
            persona=request.persona,
            deductions=request.deductions
        )

        return TaxResponse(
            tax_advice=advice,
            estimated_tax=None,
            suggestions=None
        )

    except Exception as e:
        logger.error(f"Tax advice failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(user=Depends(get_current_user)):
    logger.info(f"Analytics summary requested by user: {user.get('email', 'unknown')}")
    """
    Get analytics summary for dashboard

    Returns:
        AnalyticsResponse: Trend data and totals
    """
    try:
        logger.info("Analytics summary requested")

        # Aggregate transactions from MongoDB for this user
        transactions = list(db.transactions.find({"user_id": str(user["_id"])}))

        # Calculate totals
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        # Monthly trend data (group by month)
        from collections import defaultdict
        monthly = defaultdict(lambda: {"income": 0, "expenses": 0})
        for t in transactions:
            dt = t.get("date")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt)
            month = dt.strftime("%b")
            if t["type"] == "income":
                monthly[month]["income"] += t["amount"]
            else:
                monthly[month]["expenses"] += t["amount"]
        trend_data = [
            {"month": m, "income": v["income"], "expenses": v["expenses"]}
            for m, v in sorted(monthly.items())
        ]

        totals = {
            "income": total_income,
            "expenses": total_expenses,
            "savings": total_income - total_expenses,
            "savings_rate": ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        }

        return AnalyticsResponse(
            trend_data=trend_data,
            totals=totals
        )

    except Exception as e:
        logger.error(f"Analytics summary failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/add", response_model=TransactionResponse)
async def add_transaction(request: TransactionRequest, user=Depends(get_current_user)):
    logger.info(f"Add transaction request from user: {user.get('email', 'unknown')} | Description: {request.description}")
    """
    Add a new transaction

    Args:
        request: TransactionRequest with transaction details

    Returns:
        TransactionResponse: Success status and transaction ID
    """
    try:
        logger.info(f"Adding transaction: {request.description}")

        # Create new transaction
        new_transaction = {
            "user_id": str(user["_id"]),
            "description": request.description,
            "amount": request.amount,
            "category": request.category,
            "type": request.type,
            "date": datetime.utcnow()
        }
        result = db.transactions.insert_one(new_transaction)
        logger.info(f"Transaction added for user: {user.get('email', 'unknown')} | Transaction ID: {str(result.inserted_id)}")
        return TransactionResponse(
            success=True,
            message="Transaction added successfully",
            transaction_id=str(result.inserted_id)
        )

    except Exception as e:
        logger.error(f"Add transaction failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/recent")
async def get_recent_transactions(user=Depends(get_current_user)):
    logger.info(f"Recent transactions requested by user: {user.get('email', 'unknown')}")
    """
    Get recent transactions

    Returns:
        List of recent transactions
    """
    try:
        logger.info("Recent transactions requested")

        transactions = list(db.transactions.find({"user_id": str(user["_id"])}).sort("date", -1).limit(10))
        for txn in transactions:
            txn["id"] = str(txn["_id"])
            txn.pop("_id")
        return {"transactions": transactions}

    except Exception as e:
        logger.error(f"Get transactions failed for user {user.get('email', 'unknown')}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
