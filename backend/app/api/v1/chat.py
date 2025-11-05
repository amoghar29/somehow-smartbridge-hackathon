from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional
import uuid

from app.config.database import get_database
from app.utils.security import get_current_user
from app.models.chat import ChatSession, ChatMessage, ChatRole, ChatContext
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatSessionList,
    ChatFeedback
)
from app.ai.rag_pipeline import get_rag_pipeline

router = APIRouter(prefix="/api/v1/chat", tags=["Chat & AI Assistant"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    message: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Send a message to the AI assistant
    
    - **content**: Your message/question
    - **context**: Context type (general, goal_planning, tax_advice, investment, learning)
    - **session_id**: Optional session ID to continue conversation
    """
    
    # Get or create session
    session = await get_or_create_session(
        db,
        current_user["_id"],
        message.session_id,
        message.context
    )
    
    # Get user financial context
    user_context = await get_user_financial_context(current_user["_id"], db)
    
    # Get RAG pipeline
    rag = await get_rag_pipeline()
    
    # Search for relevant documents
    retrieved_docs = await rag.search_documents(
        query=message.content,
        user_id=current_user["_id"],
        context_type=message.context,
        n_results=3
    )
    
    # Generate AI response
    ai_response = await rag.generate_response(
        query=message.content,
        user_context=user_context,
        context_type=message.context,
        retrieved_docs=retrieved_docs
    )
    
    # Save messages to session
    user_message = ChatMessage(
        role=ChatRole.USER,
        content=message.content,
        timestamp=datetime.utcnow()
    )
    
    assistant_message = ChatMessage(
        role=ChatRole.ASSISTANT,
        content=ai_response,
        timestamp=datetime.utcnow(),
        metadata={
            "retrieved_docs_count": len(retrieved_docs),
            "context": message.context
        }
    )
    
    await db.chat_sessions.update_one(
        {"_id": session["_id"]},
        {
            "$push": {
                "messages": {
                    "$each": [
                        user_message.model_dump(),
                        assistant_message.model_dump()
                    ]
                }
            },
            "$set": {
                "updated_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            },
            "$inc": {"message_count": 2}
        }
    )
    
    # Generate suggested actions
    suggested_actions = generate_suggested_actions(
        message.content,
        message.context,
        user_context
    )
    
    return ChatMessageResponse(
        response=ai_response,
        session_id=session["session_id"],
        context=message.context,
        sources=[
            {
                "content": doc["content"][:200] + "...",
                "relevance": 1 - doc["distance"]
            }
            for doc in retrieved_docs
        ],
        suggested_actions=suggested_actions,
        timestamp=datetime.utcnow()
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get chat history for a session
    """
    
    session = await db.chat_sessions.find_one({
        "session_id": session_id,
        "user_id": current_user["_id"]
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return ChatHistoryResponse(
        session_id=session["session_id"],
        context=session["context"],
        messages=session.get("messages", []),
        created_at=session["created_at"],
        message_count=session.get("message_count", 0)
    )


@router.get("/sessions", response_model=ChatSessionList)
async def get_chat_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all chat sessions for user
    """
    
    query = {"user_id": current_user["_id"]}
    
    # Get total count
    total = await db.chat_sessions.count_documents(query)
    active_count = await db.chat_sessions.count_documents({
        **query,
        "is_active": True
    })
    
    # Get sessions
    cursor = db.chat_sessions.find(query).sort("last_activity", -1).skip(offset).limit(limit)
    sessions = await cursor.to_list(length=limit)
    
    # Format sessions
    formatted_sessions = [
        {
            "session_id": s["session_id"],
            "context": s["context"],
            "message_count": s.get("message_count", 0),
            "created_at": s["created_at"],
            "last_activity": s.get("last_activity"),
            "is_active": s.get("is_active", True)
        }
        for s in sessions
    ]
    
    return ChatSessionList(
        sessions=formatted_sessions,
        total=total,
        active_count=active_count
    )


@router.post("/feedback")
async def submit_feedback(
    feedback: ChatFeedback,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Submit feedback for a chat session
    """
    
    result = await db.chat_sessions.update_one(
        {
            "session_id": feedback.session_id,
            "user_id": current_user["_id"]
        },
        {
            "$set": {
                "user_satisfaction": feedback.rating,
                "feedback": feedback.feedback,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Feedback submitted successfully"}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a chat session"""
    
    result = await db.chat_sessions.delete_one({
        "session_id": session_id,
        "user_id": current_user["_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session deleted successfully"}


# Helper functions

async def get_or_create_session(
    db: AsyncIOMotorDatabase,
    user_id: str,
    session_id: Optional[str],
    context: ChatContext
) -> dict:
    """Get existing session or create new one"""
    
    if session_id:
        session = await db.chat_sessions.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        if session:
            return session
    
    # Create new session
    new_session = ChatSession(
        user_id=user_id,
        session_id=str(uuid.uuid4()),
        context=context
    )
    
    result = await db.chat_sessions.insert_one(
        new_session.model_dump(by_alias=True, exclude_none=True)
    )
    
    new_session.id = str(result.inserted_id)
    return new_session.model_dump(by_alias=True)


async def get_user_financial_context(user_id: str, db: AsyncIOMotorDatabase) -> dict:
    """Get user's financial context for AI"""
    
    user = await db.users.find_one({"_id": user_id})
    
    if not user:
        return {}
    
    # Get recent transactions for context
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=90)
    
    transactions = await db.transactions.find({
        "user_id": user_id,
        "date": {"$gte": start_date}
    }).to_list(None)
    
    # Calculate averages
    income_txs = [tx for tx in transactions if tx["type"] == "income"]
    expense_txs = [tx for tx in transactions if tx["type"] == "expense"]
    
    monthly_income = sum(tx["amount"] for tx in income_txs) / 3 if income_txs else 0
    monthly_expenses = sum(tx["amount"] for tx in expense_txs) / 3 if expense_txs else 0
    
    savings_rate = 0
    if monthly_income > 0:
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
    
    # Get active goals count
    active_goals = await db.goals.count_documents({
        "user_id": user_id,
        "status": "active"
    })
    
    return {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "savings_rate": savings_rate,
        "risk_profile": user.get("profile", {}).get("risk_profile", "moderate"),
        "active_goals_count": active_goals,
        "total_investments": user.get("financial_summary", {}).get("total_investments", 0),
        "occupation": user.get("profile", {}).get("occupation"),
        "age": user.get("profile", {}).get("age")
    }


def generate_suggested_actions(
    query: str,
    context: ChatContext,
    user_context: dict
) -> list:
    """Generate suggested actions based on query and context"""
    
    actions = []
    
    # Context-specific suggestions
    if context == ChatContext.GOAL_PLANNING:
        actions.append({
            "action": "create_goal",
            "label": "Create a Goal",
            "description": "Set up a new financial goal based on this discussion"
        })
    
    if context == ChatContext.INVESTMENT:
        actions.append({
            "action": "view_investments",
            "label": "View Investments",
            "description": "Check your current investment portfolio"
        })
    
    if "budget" in query.lower() or "expense" in query.lower():
        actions.append({
            "action": "view_analytics",
            "label": "View Spending Analytics",
            "description": "See detailed breakdown of your expenses"
        })
    
    if "save" in query.lower() or "saving" in query.lower():
        if user_context.get("savings_rate", 0) < 20:
            actions.append({
                "action": "create_savings_plan",
                "label": "Create Savings Plan",
                "description": "Get a personalized savings strategy"
            })
    
    return actions