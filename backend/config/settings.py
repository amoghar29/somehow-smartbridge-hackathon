"""
Configuration settings for Personal Finance Assistant Backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "model_cache"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Model configuration
# Use smaller model for faster download and testing
MODEL_ID = "gpt2"  # 500MB - Much faster to download
# MODEL_ID = "ibm-granite/granite-3.0-2b-instruct"  # 5GB - Original (uncomment when ready)
DEVICE = "cpu"
MAX_NEW_TOKENS = 300
DEFAULT_TEMPERATURE = 0.7

# Application metadata
APP_NAME = "Personal Finance Assistant"
APP_DESCRIPTION = "AI-powered financial planning and analysis backend"
APP_VERSION = "1.0.0"

# API Configuration
API_HOST = "127.0.0.1"  # Changed from 0.0.0.0 for easier browser access
API_PORT = 8000
CORS_ORIGINS = ["*"]  # Allow all origins for local development

# Environment
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
