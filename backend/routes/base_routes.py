"""
Base routes for health checks and status
"""
from fastapi import APIRouter
from models.response_models import HealthResponse
from config.settings import APP_VERSION
from core.granite_api import granite_api
from core.logger import logger

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse: Service status and version
    """
    logger.info("Health check requested")

    return HealthResponse(
        status="Backend running",
        version=APP_VERSION,
        model_loaded=granite_api.is_ready()
    )


@router.get("/health", response_model=HealthResponse)
async def detailed_health():
    """
    Detailed health check endpoint

    Returns:
        HealthResponse: Detailed service status
    """
    model_status = granite_api.is_ready()

    logger.info(f"Detailed health check - Model ready: {model_status}")

    return HealthResponse(
        status="healthy" if model_status else "model_not_loaded",
        version=APP_VERSION,
        model_loaded=model_status
    )
