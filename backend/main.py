"""
Personal Finance Assistant Backend
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import (
    APP_NAME,
    APP_DESCRIPTION,
    APP_VERSION,
    CORS_ORIGINS,
    API_HOST,
    API_PORT
)
from routes import base_routes, finance_routes, auth_router
from core.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors

    Args:
        request: FastAPI request
        exc: Exception raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )


# Include routers
app.include_router(base_routes.router, tags=["Health"])
app.include_router(finance_routes.router, tags=["Finance"])
app.include_router(auth_router, tags=["Auth"])


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"API documentation available at http://{API_HOST}:{API_PORT}/docs")

    # Initialize AI model (will load on first use)
    try:
        from core.granite_api import granite_api
        logger.info("AI model will be loaded on first request")
    except Exception as e:
        logger.error(f"Failed to initialize AI model: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info(f"Shutting down {APP_NAME}")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
