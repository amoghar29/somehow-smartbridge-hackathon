# MongoDB Integration Setup Guide

This guide will help you set up MongoDB for the Personal Finance Assistant backend.

## Prerequisites

You have two options for running MongoDB:

### Option 1: MongoDB Atlas (Cloud - Recommended for Quick Start)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Get your connection string
4. Add your IP address to the whitelist
5. Create a database user with username and password

### Option 2: Local MongoDB Installation

1. Download and install MongoDB Community Edition from [MongoDB Downloads](https://www.mongodb.com/try/download/community)
2. Start MongoDB service:
   - **Windows**: MongoDB should start automatically, or run `mongod` from command prompt
   - **Mac/Linux**: Run `sudo systemctl start mongod` or `brew services start mongodb-community`

## Configuration

### 1. Install Python Dependencies

```bash
cd backend
pip install motor pymongo dnspython
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env` file in the `backend` directory:

**For MongoDB Atlas (Cloud):**

```env
# MongoDB Atlas Connection
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=finance_assistant
```

Replace `username`, `password`, and `cluster0.xxxxx.mongodb.net` with your actual Atlas credentials.

**For Local MongoDB:**

```env
# Local MongoDB Connection
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=finance_assistant
```

### 3. Verify Connection

Start the backend server:

```bash
cd backend
python main.py
```

Look for these log messages:

```
Connected to MongoDB at mongodb://localhost:27017
Using database: finance_assistant
MongoDB connection initialized
```

If you see these messages, MongoDB is connected successfully! ✅

## Database Structure

The application uses the following collections:

### Collections

1. **transactions** - Stores all financial transactions
   - Fields: description, amount, category, type, date, created_at, updated_at

2. **chat_history** - Stores AI chat interactions
   - Fields: question, response, persona, timestamp, metadata

3. **goals** - Stores financial goals (future feature)
   - Fields: name, target_amount, current_amount, category, deadline, status

4. **users** - Stores user accounts (future feature)
   - Fields: email, name, preferences

## Features

### Automatic Fallback

The application includes automatic fallback to JSON files if MongoDB is not available:

- ✅ **MongoDB Connected**: All data is saved to and loaded from MongoDB
- ⚠️ **MongoDB Not Available**: Falls back to JSON files in `backend/data/` directory

This means the application will work even without MongoDB, but data won't persist between restarts without a database.

### Chat History Storage

Every AI interaction is automatically saved to MongoDB:

- Question asked by user
- AI response
- User persona (professional/conservative/aggressive)
- Timestamp
- Additional metadata

You can view chat history by querying the `chat_history` collection.

### Transaction Storage

All transactions are stored in MongoDB with full CRUD support:

- Create new transactions via `/transactions/add`
- Retrieve transactions via `/transactions/recent`
- Automatic analytics calculation
- Date-based sorting (newest first)

## Viewing Your Data

### Using MongoDB Compass (GUI - Recommended)

1. Download [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. Connect using your connection string
3. Browse collections: `transactions`, `chat_history`, etc.

### Using MongoDB Shell

```bash
# Connect to local MongoDB
mongosh

# Switch to your database
use finance_assistant

# View transactions
db.transactions.find().pretty()

# View chat history
db.chat_history.find().pretty()

# Count documents
db.transactions.countDocuments()
```

### Using Python Script

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.finance_assistant

# Get all transactions
transactions = list(db.transactions.find())
print(f"Total transactions: {len(transactions)}")

# Get recent chat messages
chats = list(db.chat_history.find().sort("timestamp", -1).limit(10))
for chat in chats:
    print(f"Q: {chat['question']}")
    print(f"A: {chat['response'][:100]}...")
```

## Troubleshooting

### Connection Failed

**Error**: `Failed to connect to MongoDB`

**Solutions**:
1. Verify MongoDB is running: `mongosh` (should connect)
2. Check MONGODB_URL in `.env` file
3. For Atlas: Verify IP whitelist and credentials
4. Check firewall settings

### Authentication Failed

**Error**: `Authentication failed`

**Solutions**:
1. Verify username/password in connection string
2. Check database user permissions in Atlas
3. Ensure special characters in password are URL-encoded

### Import Error

**Error**: `ModuleNotFoundError: No module named 'motor'`

**Solution**:
```bash
pip install motor pymongo dnspython
```

## Next Steps

1. ✅ MongoDB is now integrated
2. ✅ Transactions are being saved to database
3. ✅ Chat history is being recorded
4. 🔄 Use MongoDB Compass to view your data
5. 🔄 Query analytics from stored transactions

## Support

For MongoDB Atlas support: https://www.mongodb.com/docs/atlas/
For MongoDB Community support: https://www.mongodb.com/docs/manual/
