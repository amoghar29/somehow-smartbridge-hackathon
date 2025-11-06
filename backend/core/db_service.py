"""
Database service layer for MongoDB operations
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from core.database import get_db
from core.logger import logger
from config.settings import (
    COLLECTION_TRANSACTIONS,
    COLLECTION_CHAT_HISTORY,
    COLLECTION_GOALS
)


class TransactionService:
    """Service for transaction database operations"""

    @staticmethod
    async def create_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new transaction in the database

        Args:
            transaction_data: Transaction data dictionary

        Returns:
            Created transaction with ID
        """
        try:
            db = get_db()
            if db is None:
                logger.warning("Database not connected, cannot create transaction")
                return {"success": False, "error": "Database not connected"}

            # Add timestamps
            transaction_data["created_at"] = datetime.utcnow()
            transaction_data["updated_at"] = datetime.utcnow()

            collection = db[COLLECTION_TRANSACTIONS]
            result = await collection.insert_one(transaction_data)

            logger.info(f"Transaction created with ID: {result.inserted_id}")

            return {
                "success": True,
                "transaction_id": str(result.inserted_id),
                "message": "Transaction created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_transactions(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get transactions from database

        Args:
            limit: Maximum number of transactions to return
            skip: Number of transactions to skip

        Returns:
            List of transactions
        """
        try:
            db = get_db()
            if db is None:
                logger.warning("Database not connected, returning empty list")
                return []

            collection = db[COLLECTION_TRANSACTIONS]

            # Get transactions sorted by date (newest first)
            cursor = collection.find().sort("created_at", -1).skip(skip).limit(limit)
            transactions = await cursor.to_list(length=limit)

            # Convert ObjectId to string
            for txn in transactions:
                txn["id"] = str(txn.pop("_id"))

            logger.info(f"Retrieved {len(transactions)} transactions from database")
            return transactions

        except Exception as e:
            logger.error(f"Error retrieving transactions: {str(e)}")
            return []

    @staticmethod
    async def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a single transaction by ID"""
        try:
            from bson import ObjectId

            db = get_db()
            if db is None:
                return None

            collection = db[COLLECTION_TRANSACTIONS]
            transaction = await collection.find_one({"_id": ObjectId(transaction_id)})

            if transaction:
                transaction["id"] = str(transaction.pop("_id"))

            return transaction

        except Exception as e:
            logger.error(f"Error retrieving transaction: {str(e)}")
            return None


class ChatHistoryService:
    """Service for chat history database operations"""

    @staticmethod
    async def save_chat_message(question: str, response: str, persona: str = "professional",
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Save a chat interaction to database

        Args:
            question: User's question
            response: AI's response
            persona: User persona
            metadata: Additional metadata

        Returns:
            Result dictionary
        """
        try:
            db = get_db()
            if db is None:
                logger.warning("Database not connected, cannot save chat message")
                return {"success": False, "error": "Database not connected"}

            chat_data = {
                "question": question,
                "response": response,
                "persona": persona,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }

            collection = db[COLLECTION_CHAT_HISTORY]
            result = await collection.insert_one(chat_data)

            logger.info(f"Chat message saved with ID: {result.inserted_id}")

            return {
                "success": True,
                "message_id": str(result.inserted_id)
            }

        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_chat_history(limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get chat history from database

        Args:
            limit: Maximum number of messages to return
            skip: Number of messages to skip

        Returns:
            List of chat messages
        """
        try:
            db = get_db()
            if db is None:
                return []

            collection = db[COLLECTION_CHAT_HISTORY]

            # Get messages sorted by timestamp (newest first)
            cursor = collection.find().sort("timestamp", -1).skip(skip).limit(limit)
            messages = await cursor.to_list(length=limit)

            # Convert ObjectId to string
            for msg in messages:
                msg["id"] = str(msg.pop("_id"))

            logger.info(f"Retrieved {len(messages)} chat messages from database")
            return messages

        except Exception as e:
            logger.error(f"Error retrieving chat history: {str(e)}")
            return []


class GoalService:
    """Service for goals database operations"""

    @staticmethod
    async def create_goal(goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new goal in the database"""
        try:
            db = get_db()
            if db is None:
                return {"success": False, "error": "Database not connected"}

            goal_data["created_at"] = datetime.utcnow()
            goal_data["updated_at"] = datetime.utcnow()
            goal_data["status"] = goal_data.get("status", "active")

            collection = db[COLLECTION_GOALS]
            result = await collection.insert_one(goal_data)

            logger.info(f"Goal created with ID: {result.inserted_id}")

            return {
                "success": True,
                "goal_id": str(result.inserted_id)
            }

        except Exception as e:
            logger.error(f"Error creating goal: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_goals(status: str = "active") -> List[Dict[str, Any]]:
        """Get goals from database"""
        try:
            db = get_db()
            if db is None:
                return []

            collection = db[COLLECTION_GOALS]

            query = {"status": status} if status else {}
            cursor = collection.find(query).sort("created_at", -1)
            goals = await cursor.to_list(length=100)

            for goal in goals:
                goal["id"] = str(goal.pop("_id"))

            return goals

        except Exception as e:
            logger.error(f"Error retrieving goals: {str(e)}")
            return []

    @staticmethod
    async def update_goal(goal_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a goal in the database"""
        try:
            from bson import ObjectId

            db = get_db()
            if db is None:
                return {"success": False, "error": "Database not connected"}

            update_data["updated_at"] = datetime.utcnow()

            collection = db[COLLECTION_GOALS]
            result = await collection.update_one(
                {"_id": ObjectId(goal_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Goal updated: {goal_id}")
                return {
                    "success": True,
                    "goal_id": goal_id,
                    "message": "Goal updated successfully"
                }
            else:
                return {"success": False, "error": "Goal not found or no changes made"}

        except Exception as e:
            logger.error(f"Error updating goal: {str(e)}")
            return {"success": False, "error": str(e)}
