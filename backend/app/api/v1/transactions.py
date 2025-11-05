from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, List
from bson import ObjectId

from app.config.database import get_database
from app.utils.security import get_current_user
from app.models.transaction import TransactionModel, TransactionType, TransactionCategory
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionAnalytics
)

router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new transaction
    
    - **type**: income, expense, investment, or savings
    - **category**: Transaction category (food, transport, salary, etc.)
    - **amount**: Transaction amount (must be positive)
    - **description**: Transaction description
    """
    # Create transaction model
    transaction_model = TransactionModel(
        user_id=current_user["_id"],
        **transaction.model_dump()
    )
    
    # Insert into database
    result = await db.transactions.insert_one(
        transaction_model.model_dump(by_alias=True)
    )
    
    # Update user financial summary
    await update_user_financial_summary(current_user["_id"], db)
    
    return {
        "id": str(result.inserted_id),
        "message": "Transaction created successfully"
    }


@router.get("/", response_model=TransactionList)
async def get_transactions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[TransactionCategory] = None,
    type: Optional[TransactionType] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get user transactions with filters
    
    - **limit**: Number of transactions to return (max 100)
    - **offset**: Pagination offset
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **category**: Filter by category
    - **type**: Filter by type
    """
    # Build query
    query = {"user_id": current_user["_id"]}
    
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
    
    if category:
        query["category"] = category
    
    if type:
        query["type"] = type
    
    # Get total count
    total = await db.transactions.count_documents(query)
    
    # Get transactions
    cursor = db.transactions.find(query).sort("date", -1).skip(offset).limit(limit)
    transactions = await cursor.to_list(length=limit)
    
    # Convert to response format
    transaction_responses = [
        TransactionResponse(
            id=str(tx["_id"]),
            user_id=tx["user_id"],
            type=tx["type"],
            category=tx["category"],
            amount=tx["amount"],
            description=tx["description"],
            date=tx["date"],
            payment_method=tx.get("payment_method"),
            tags=tx.get("tags", []),
            created_at=tx["created_at"]
        )
        for tx in transactions
    ]
    
    return TransactionList(
        transactions=transaction_responses,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific transaction by ID"""
    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )
    
    transaction = await db.transactions.find_one({
        "_id": transaction_id,
        "user_id": current_user["_id"]
    })
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a transaction"""
    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )
    
    # Check if transaction exists
    existing = await db.transactions.find_one({
        "_id": transaction_id,
        "user_id": current_user["_id"]
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update transaction
    update_data = {
        k: v for k, v in transaction_update.model_dump(exclude_unset=True).items()
        if v is not None
    }
    update_data["updated_at"] = datetime.utcnow()
    
    await db.transactions.update_one(
        {"_id": transaction_id},
        {"$set": update_data}
    )
    
    # Update user financial summary
    await update_user_financial_summary(current_user["_id"], db)
    
    return {"message": "Transaction updated successfully"}


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a transaction"""
    if not ObjectId.is_valid(transaction_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )
    
    result = await db.transactions.delete_one({
        "_id": transaction_id,
        "user_id": current_user["_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update user financial summary
    await update_user_financial_summary(current_user["_id"], db)
    
    return {"message": "Transaction deleted successfully"}


@router.get("/analytics/summary", response_model=TransactionAnalytics)
async def get_analytics(
    period: str = Query("monthly", regex="^(daily|weekly|monthly|yearly)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get spending analytics
    
    - **period**: daily, weekly, monthly, or yearly
    """
    # Calculate date range
    now = datetime.utcnow()
    
    if period == "daily":
        start_date = now - timedelta(days=1)
    elif period == "weekly":
        start_date = now - timedelta(weeks=1)
    elif period == "monthly":
        start_date = now - timedelta(days=30)
    else:  # yearly
        start_date = now - timedelta(days=365)
    
    # Get transactions
    transactions = await db.transactions.find({
        "user_id": current_user["_id"],
        "date": {"$gte": start_date}
    }).to_list(None)
    
    # Calculate analytics
    total_income = sum(tx["amount"] for tx in transactions if tx["type"] == "income")
    total_expenses = sum(tx["amount"] for tx in transactions if tx["type"] == "expense")
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Category breakdown
    category_breakdown = {}
    for tx in transactions:
        if tx["type"] == "expense":
            cat = tx["category"]
            if cat not in category_breakdown:
                category_breakdown[cat] = {"amount": 0, "count": 0}
            category_breakdown[cat]["amount"] += tx["amount"]
            category_breakdown[cat]["count"] += 1
    
    # Add percentages
    for cat in category_breakdown:
        category_breakdown[cat]["percentage"] = (
            category_breakdown[cat]["amount"] / total_expenses * 100
            if total_expenses > 0 else 0
        )
    
    return TransactionAnalytics(
        period=period,
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        category_breakdown=category_breakdown,
        monthly_trend=[],  # To be implemented
        anomalies=[]  # To be implemented
    )


async def update_user_financial_summary(user_id: str, db: AsyncIOMotorDatabase):
    """Update user's financial summary"""
    # Get all transactions
    transactions = await db.transactions.find({"user_id": user_id}).to_list(None)
    
    total_income = sum(tx["amount"] for tx in transactions if tx["type"] == "income")
    total_expenses = sum(tx["amount"] for tx in transactions if tx["type"] == "expense")
    total_savings = sum(tx["amount"] for tx in transactions if tx["type"] == "savings")
    
    # Get investments
    investments = await db.investments.find({"user_id": user_id}).to_list(None)
    total_investments = sum(inv.get("current_value", inv["amount_invested"]) for inv in investments)
    
    net_worth = total_savings + total_investments
    
    # Update user document
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "financial_summary": {
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "total_savings": total_savings,
                    "total_investments": total_investments,
                    "net_worth": net_worth
                },
                "updated_at": datetime.utcnow()
            }
        }
    )