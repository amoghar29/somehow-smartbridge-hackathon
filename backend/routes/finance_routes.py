"""
Finance-related API routes
"""
from fastapi import APIRouter, HTTPException
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

router = APIRouter()


@router.post("/ai/generate", response_model=ChatResponse)
async def generate_ai_response(request: ChatRequest):
    """
    General AI response endpoint

    Args:
        request: ChatRequest with question and persona

    Returns:
        ChatResponse: AI-generated response
    """
    try:
        logger.info(f"AI generate request: {request.question[:50]}...")

        # Route to appropriate agent based on intent
        intent = route_intent(request.question)

        if intent == 'general':
            # Use AI for general queries
            prompt = f"""You are a helpful personal finance assistant. Answer this question concisely and accurately.

Question: {request.question}

Provide a clear, helpful answer in 2-3 sentences."""

            response_text = generate(prompt, max_new_tokens=150, temperature=0.7)
        else:
            # Provide guidance for specific intents
            response_text = get_fallback_response(request.question)

        return ChatResponse(response=response_text)

    except Exception as e:
        logger.error(f"AI generate failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/budget-summary", response_model=BudgetResponse)
async def get_budget_summary(request: BudgetRequest):
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
        logger.error(f"Budget analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/goal-planner", response_model=GoalResponse)
async def plan_financial_goal(request: GoalRequest):
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
        logger.error(f"Goal planning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/tax-advice", response_model=TaxResponse)
async def get_tax_advisory(request: TaxRequest):
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
        logger.error(f"Tax advice failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary():
    """
    Get analytics summary for dashboard

    Returns:
        AnalyticsResponse: Trend data and totals
    """
    try:
        logger.info("Analytics summary requested")

        # Load sample transactions
        transactions_file = DATA_DIR / "sample_transactions.json"

        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
        else:
            transactions = []

        # Calculate totals
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        # Create trend data (simplified)
        trend_data = [
            {"month": "Jan", "income": total_income * 0.9, "expenses": total_expenses * 0.85},
            {"month": "Feb", "income": total_income * 0.95, "expenses": total_expenses * 0.90},
            {"month": "Mar", "income": total_income, "expenses": total_expenses}
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
        logger.error(f"Analytics summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/add", response_model=TransactionResponse)
async def add_transaction(request: TransactionRequest):
    """
    Add a new transaction

    Args:
        request: TransactionRequest with transaction details

    Returns:
        TransactionResponse: Success status and transaction ID
    """
    try:
        logger.info(f"Adding transaction: {request.description}")

        # Load existing transactions
        transactions_file = DATA_DIR / "sample_transactions.json"

        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
        else:
            transactions = []

        # Create new transaction
        new_transaction = {
            "id": f"txn_{len(transactions) + 1}",
            "description": request.description,
            "amount": request.amount,
            "category": request.category,
            "type": request.type,
            "date": datetime.now().isoformat()
        }

        transactions.append(new_transaction)

        # Save back to file
        with open(transactions_file, 'w') as f:
            json.dump(transactions, f, indent=2)

        return TransactionResponse(
            success=True,
            message="Transaction added successfully",
            transaction_id=new_transaction["id"]
        )

    except Exception as e:
        logger.error(f"Add transaction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/recent")
async def get_recent_transactions():
    """
    Get recent transactions

    Returns:
        List of recent transactions
    """
    try:
        logger.info("Recent transactions requested")

        transactions_file = DATA_DIR / "sample_transactions.json"

        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
        else:
            transactions = []

        # Return last 10 transactions
        return {"transactions": transactions[-10:]}

    except Exception as e:
        logger.error(f"Get transactions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
