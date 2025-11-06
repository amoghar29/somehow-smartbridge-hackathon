"""
MongoDB database connection and management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional
from config.settings import MONGODB_URL, MONGODB_DB_NAME
from core.logger import logger


class Database:
    """MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {MONGODB_URL}")
            logger.info(f"Using database: {MONGODB_DB_NAME}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            logger.warning("Application will continue without database. Data will not persist.")
            cls.client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            cls.client = None

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        if cls.client is None:
            logger.warning("Database client is not connected")
            return None
        return cls.client[MONGODB_DB_NAME]

    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected"""
        return cls.client is not None


# Helper function to get database
def get_db():
    """Get database instance"""
    return Database.get_database()
