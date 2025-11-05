from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

from app.config.database import get_database
from app.utils.security import get_current_user
from app.models.goal import GoalModel, GoalStatus, SavingStrategy
from app.schemas.goal import (
    GoalPlanRequest,
    GoalCreate,
    GoalUpdate,
    GoalContribution,
    GoalResponse,
    GoalPlanResponse,
    GoalProgressResponse,
    GoalListResponse
)
from app.services.goal_planner import GoalPlannerService

router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])


@router.post("/plan", response_model=GoalPlanResponse)
async def create_goal_plan(
    goal_request: GoalPlanRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate AI-powered goal plan with multiple strategies
    
    - **name**: Goal name
    - **target_amount**: Target amount to save
    - **current_amount**: Amount already saved (optional)
    - **target_date**: When you want to achieve the goal
    - **category**: Goal category (travel, education, home, etc.)
    """
    
    planner = GoalPlannerService(db)
    
    plan = await planner.generate_goal_plan(
        goal_request.model_dump(),
        current_user["_id"]
    )
    
    return GoalPlanResponse(**plan)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new financial goal
    
    - **name**: Goal name
    - **target_amount**: Target amount
    - **saving_strategy**: easy, moderate, or aggressive
    - **monthly_contribution**: Monthly saving amount
    """
    
    # Determine goal type based on timeline
    months_to_goal = (goal.target_date - datetime.utcnow()).days / 30
    
    if months_to_goal < 12:
        goal_type = "short_term"
    elif months_to_goal < 36:
        goal_type = "medium_term"
    else:
        goal_type = "long_term"
    
    # Create goal model
    goal_model = GoalModel(
        user_id=current_user["_id"],
        type=goal_type,
        start_date=datetime.utcnow(),
        **goal.model_dump()
    )
    
    # Calculate initial progress
    if goal_model.target_amount > 0:
        goal_model.progress_percentage = (
            goal_model.current_amount / goal_model.target_amount * 100
        )
    
    # Insert into database
    result = await db.goals.insert_one(
        goal_model.model_dump(by_alias=True, exclude_none=True)
    )
    
    return {
        "id": str(result.inserted_id),
        "message": "Goal created successfully"
    }


@router.get("/", response_model=GoalListResponse)
async def get_goals(
    status: Optional[GoalStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all user goals
    
    - **status**: Filter by status (active, completed, paused)
    - **limit**: Number of goals to return
    - **offset**: Pagination offset
    """
    
    # Build query
    query = {"user_id": current_user["_id"]}
    if status:
        query["status"] = status
    
    # Get total count
    total = await db.goals.count_documents(query)
    active_count = await db.goals.count_documents({
        "user_id": current_user["_id"],
        "status": "active"
    })
    completed_count = await db.goals.count_documents({
        "user_id": current_user["_id"],
        "status": "completed"
    })
    
    # Get goals
    cursor = db.goals.find(query).sort("created_at", -1).skip(offset).limit(limit)
    goals = await cursor.to_list(length=limit)
    
    # Convert to response format
    goal_responses = [
        GoalResponse(
            id=str(goal["_id"]),
            user_id=goal["user_id"],
            name=goal["name"],
            description=goal.get("description"),
            target_amount=goal["target_amount"],
            current_amount=goal["current_amount"],
            progress_percentage=goal.get("progress_percentage", 0),
            target_date=goal["target_date"],
            status=goal["status"],
            category=goal["category"],
            saving_strategy=goal["saving_strategy"],
            monthly_contribution=goal["monthly_contribution"],
            created_at=goal["created_at"]
        )
        for goal in goals
    ]
    
    return GoalListResponse(
        goals=goal_responses,
        total=total,
        active_count=active_count,
        completed_count=completed_count
    )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific goal by ID"""
    
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID"
        )
    
    goal = await db.goals.find_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    return GoalResponse(
        id=str(goal["_id"]),
        user_id=goal["user_id"],
        name=goal["name"],
        description=goal.get("description"),
        target_amount=goal["target_amount"],
        current_amount=goal["current_amount"],
        progress_percentage=goal.get("progress_percentage", 0),
        target_date=goal["target_date"],
        status=goal["status"],
        category=goal["category"],
        saving_strategy=goal["saving_strategy"],
        monthly_contribution=goal["monthly_contribution"],
        created_at=goal["created_at"]
    )


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed goal progress with analytics
    """
    
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID"
        )
    
    goal = await db.goals.find_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Calculate progress
    planner = GoalPlannerService(db)
    progress = await planner.calculate_goal_progress(goal)
    
    # Get milestones
    milestones = goal.get("milestones", [])
    
    # Generate visualization data
    visualization_data = generate_progress_visualization(goal, progress)
    
    return GoalProgressResponse(
        goal=GoalResponse(
            id=str(goal["_id"]),
            user_id=goal["user_id"],
            name=goal["name"],
            description=goal.get("description"),
            target_amount=goal["target_amount"],
            current_amount=goal["current_amount"],
            progress_percentage=goal.get("progress_percentage", 0),
            target_date=goal["target_date"],
            status=goal["status"],
            category=goal["category"],
            saving_strategy=goal["saving_strategy"],
            monthly_contribution=goal["monthly_contribution"],
            created_at=goal["created_at"]
        ),
        progress=progress,
        milestones=milestones,
        visualization_data=visualization_data,
        on_track=progress["on_track"],
        projected_completion=progress.get("projected_completion")
    )


@router.put("/{goal_id}")
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a goal"""
    
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID"
        )
    
    # Check if goal exists
    existing = await db.goals.find_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Update goal
    update_data = {
        k: v for k, v in goal_update.model_dump(exclude_unset=True).items()
        if v is not None
    }
    update_data["updated_at"] = datetime.utcnow()
    
    await db.goals.update_one(
        {"_id": goal_id},
        {"$set": update_data}
    )
    
    return {"message": "Goal updated successfully"}


@router.post("/{goal_id}/contribute")
async def add_contribution(
    goal_id: str,
    contribution: GoalContribution,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Add a contribution to a goal
    
    - **amount**: Contribution amount
    - **note**: Optional note about the contribution
    """
    
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID"
        )
    
    # Get goal
    goal = await db.goals.find_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Update goal
    new_amount = goal["current_amount"] + contribution.amount
    new_progress = (new_amount / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
    
    # Check if goal is completed
    new_status = goal["status"]
    completed_at = goal.get("completed_at")
    
    if new_amount >= goal["target_amount"] and goal["status"] == "active":
        new_status = "completed"
        completed_at = datetime.utcnow()
    
    # Add to milestones
    milestone = {
        "date": datetime.utcnow(),
        "amount": new_amount,
        "percentage": new_progress,
        "contribution": contribution.amount,
        "note": contribution.note
    }
    
    await db.goals.update_one(
        {"_id": goal_id},
        {
            "$set": {
                "current_amount": new_amount,
                "progress_percentage": new_progress,
                "status": new_status,
                "completed_at": completed_at,
                "last_contribution_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            "$push": {"milestones": milestone},
            "$inc": {"total_contributed": contribution.amount}
        }
    )
    
    return {
        "message": "Contribution added successfully",
        "new_amount": new_amount,
        "progress_percentage": new_progress,
        "status": new_status
    }


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a goal"""
    
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID"
        )
    
    result = await db.goals.delete_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    return {"message": "Goal deleted successfully"}


def generate_progress_visualization(goal: dict, progress: dict) -> dict:
    """Generate visualization data for goal progress"""
    
    # Timeline data points
    start_date = goal["start_date"]
    target_date = goal["target_date"]
    current_date = datetime.utcnow()
    
    # Generate monthly checkpoints
    checkpoints = []
    months = int((target_date - start_date).days / 30)
    
    for i in range(months + 1):
        checkpoint_date = start_date + (target_date - start_date) * (i / months)
        expected_amount = goal["target_amount"] * (i / months)
        
        checkpoints.append({
            "date": checkpoint_date.isoformat(),
            "expected_amount": round(expected_amount, 2),
            "month": i
        })
    
    # Actual progress points from milestones
    actual_progress = [
        {
            "date": milestone["date"].isoformat(),
            "amount": milestone["amount"]
        }
        for milestone in goal.get("milestones", [])
    ]
    
    return {
        "timeline": {
            "start_date": start_date.isoformat(),
            "target_date": target_date.isoformat(),
            "current_date": current_date.isoformat()
        },
        "checkpoints": checkpoints,
        "actual_progress": actual_progress,
        "status_color": "green" if progress["on_track"] else "red" if progress["status"] == "behind" else "yellow"
    }