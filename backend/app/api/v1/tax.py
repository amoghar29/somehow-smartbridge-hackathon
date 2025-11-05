from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.utils.security import get_current_user
from app.services.tax_advisor import TaxAdvisorService

router = APIRouter(prefix="/api/v1/tax", tags=["Tax Planning"])


@router.get("/suggestions")
async def get_tax_suggestions(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get tax-saving suggestions"""
    service = TaxAdvisorService(db)
    suggestions = await service.generate_tax_saving_suggestions(current_user["_id"])
    return suggestions
