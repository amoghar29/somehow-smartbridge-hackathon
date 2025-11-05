from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import Redis
from typing import Optional
from app.config.settings import settings


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[Redis] = None
    
    async def connect(self):
        """Connect to databases"""
        # MongoDB
        self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.mongo_client[settings.MONGODB_DB_NAME]
        
        # Create indexes
        await self.create_indexes()
        
        # Redis
        self.redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        print("✅ Connected to MongoDB and Redis")
    
    async def close(self):
        """Close database connections"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.redis_client:
            await self.redis_client.close()
        print("👋 Disconnected from databases")
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        # Users collection
        await self.db.users.create_index("email", unique=True)
        await self.db.users.create_index("username", unique=True)
        
        # Transactions collection
        await self.db.transactions.create_index([("user_id", 1), ("date", -1)])
        await self.db.transactions.create_index([("user_id", 1), ("category", 1)])
        await self.db.transactions.create_index([("user_id", 1), ("type", 1)])
        
        # Goals collection
        await self.db.goals.create_index([("user_id", 1), ("status", 1)])
        await self.db.goals.create_index([("user_id", 1), ("target_date", 1)])
        
        # Investments collection
        await self.db.investments.create_index([("user_id", 1), ("type", 1)])
        
        # Chat sessions collection
        await self.db.chat_sessions.create_index([("user_id", 1), ("session_id", 1)])
        await self.db.chat_sessions.create_index([("user_id", 1), ("is_active", 1)])
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        return self.db
    
    def get_redis(self) -> Redis:
        """Get Redis instance"""
        return self.redis_client


# Global database manager instance
db_manager = DatabaseManager()


async def init_db():
    """Initialize database connection"""
    await db_manager.connect()


async def close_db():
    """Close database connection"""
    await db_manager.close()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency for getting database"""
    return db_manager.get_database()


async def get_redis() -> Redis:
    """Dependency for getting Redis"""
    return db_manager.get_redis()