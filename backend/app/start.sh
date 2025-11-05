#!/bin/bash

# Startup script for Personal Finance Bot Backend

echo "🚀 Starting Personal Finance Bot Backend..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file. Please update it with your configuration.${NC}"
        echo -e "${RED}❌ Exiting. Please configure .env file first.${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! nc -z localhost 27017 2>/dev/null; then
    echo -e "${RED}❌ MongoDB is not running on localhost:27017${NC}"
    echo "Please start MongoDB first:"
    echo "  sudo systemctl start mongod"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB is running${NC}"

# Check if Redis is running
echo "Checking Redis connection..."
if ! nc -z localhost 6379 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Redis is not running on localhost:6379${NC}"
    echo "Redis is optional but recommended for caching"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    uv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
uv pip install -e .

# Create necessary directories
echo "Creating directories..."
mkdir -p data/embeddings
mkdir -p logs
mkdir -p uploads

# Run database migrations (if any)
# echo "Running database setup..."
# python -m app.scripts.init_db

# Determine run mode
MODE=${1:-dev}

if [ "$MODE" = "dev" ]; then
    echo -e "${GREEN}🔧 Starting in DEVELOPMENT mode...${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
elif [ "$MODE" = "prod" ]; then
    echo -e "${GREEN}🚀 Starting in PRODUCTION mode...${NC}"
    gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --log-level info \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log
else
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo "Usage: ./start.sh [dev|prod]"
    exit 1
fi