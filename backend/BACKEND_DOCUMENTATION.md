# Backend Development Documentation

## Table of Contents
1. [Database Schemas](#database-schemas)
2. [API Endpoints](#api-endpoints)
3. [RAG Pipeline Implementation](#rag-pipeline-implementation)
4. [Service Layer Implementation](#service-layer-implementation)
5. [Authentication & Security](#authentication--security)
6. [System Prompts & AI Configuration](#system-prompts--ai-configuration)

## 📊 Database Schemas

### MongoDB Collections

#### 1. Users Collection
```python
# backend/app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, List
from bson import ObjectId

class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    full_name: str
    phone_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Profile Information
    profile: Dict = {
        "age": None,
        "occupation": None,
        "annual_income": None,
        "risk_profile": "moderate",  # conservative, moderate, aggressive
        "financial_goals": []
    }
    
    # Preferences
    preferences: Dict = {
        "currency": "INR",
        "notification_enabled": True,
        "email_alerts": True,
        "savings_reminder": True
    }
    
    # Financial Summary
    financial_summary: Dict = {
        "total_income": 0,
        "total_expenses": 0,
        "total_savings": 0,
        "total_investments": 0,
        "net_worth": 0
    }
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
```

#### 2. Transactions Collection
```python
# backend/app/models/transaction.py
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    INVESTMENT = "investment"
    SAVINGS = "savings"

class TransactionCategory(str, Enum):
    SALARY = "salary"
    FOOD = "food"
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RENT = "rent"
    EMI = "emi"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    OTHER = "other"

class TransactionModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    type: TransactionType
    category: TransactionCategory
    amount: float
    description: str
    date: datetime
    payment_method: Optional[str] = None  # cash, card, upi, bank_transfer
    tags: List[str] = []
    recurring: bool = False
    recurring_frequency: Optional[str] = None  # daily, weekly, monthly, yearly
    
    # For email parsing
    source: Optional[str] = None  # manual, email, bank_sync
    email_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI Analysis
    ai_insights: Optional[Dict] = None
    anomaly_flag: bool = False
```

#### 3. Goals Collection
```python
# backend/app/models/goal.py
class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class GoalType(str, Enum):
    SHORT_TERM = "short_term"  # < 1 year
    MEDIUM_TERM = "medium_term"  # 1-3 years
    LONG_TERM = "long_term"  # > 3 years

class SavingStrategy(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class GoalModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0
    start_date: datetime
    target_date: datetime
    type: GoalType
    status: GoalStatus = GoalStatus.ACTIVE
    category: str  # education, travel, emergency, retirement, etc.
    
    # Savings Plan
    saving_strategy: SavingStrategy
    monthly_contribution: float
    contribution_frequency: str = "monthly"
    
    # Progress Tracking
    milestones: List[Dict] = []  # [{date, amount, percentage}]
    progress_percentage: float = 0
    
    # AI Recommendations
    ai_plan: Dict = {
        "recommended_monthly_saving": 0,
        "investment_suggestions": [],
        "feasibility_score": 0,
        "risk_assessment": "",
        "alternative_strategies": []
    }
    
    # Notifications
    reminder_enabled: bool = True
    last_reminder: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 4. Chat History Collection
```python
# backend/app/models/chat.py
class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatContext(str, Enum):
    GENERAL = "general"
    GOAL_PLANNING = "goal_planning"
    TAX_ADVICE = "tax_advice"
    INVESTMENT = "investment"
    LEARNING = "learning"

class ChatMessage(BaseModel):
    role: ChatRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = None

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    session_id: str
    context: ChatContext
    messages: List[ChatMessage] = []
    
    # RAG Context
    retrieved_documents: List[Dict] = []
    embeddings_used: List[str] = []
    
    # Session Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Analytics
    user_satisfaction: Optional[int] = None  # 1-5 rating
    feedback: Optional[str] = None
```

#### 5. Investments Collection
```python
# backend/app/models/investment.py
class InvestmentType(str, Enum):
    STOCKS = "stocks"
    MUTUAL_FUNDS = "mutual_funds"
    FIXED_DEPOSIT = "fixed_deposit"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    BONDS = "bonds"
    PPF = "ppf"
    NPS = "nps"
    OTHER = "other"

class InvestmentModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    type: InvestmentType
    name: str
    amount_invested: float
    current_value: float
    purchase_date: datetime
    maturity_date: Optional[datetime] = None
    returns_percentage: float = 0
    
    # Details
    units: Optional[float] = None
    nav: Optional[float] = None  # For mutual funds
    interest_rate: Optional[float] = None  # For FD, bonds
    
    # Tracking
    performance_history: List[Dict] = []  # [{date, value, returns}]
    dividends_received: float = 0
    
    # Risk Metrics
    risk_level: str = "moderate"  # low, moderate, high
    liquidity: str = "medium"  # high, medium, low
    
    # Tax Information
    tax_category: str  # equity, debt, etc.
    lock_in_period: Optional[int] = None  # in months
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## 🔌 API Endpoints

### Authentication Endpoints
```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Register a new user"""
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create user
    user = UserModel(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    
    await db.users.insert_one(user.dict(by_alias=True))
    return {"message": "User registered successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user["_id"]})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Transaction Management Endpoints
```python
# backend/app/api/v1/transactions.py
router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])

@router.post("/")
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new transaction"""
    transaction_model = TransactionModel(
        user_id=current_user["_id"],
        **transaction.dict()
    )
    
    # AI Analysis
    transaction_model.ai_insights = await analyze_transaction(transaction_model)
    
    result = await db.transactions.insert_one(transaction_model.dict(by_alias=True))
    
    # Update user financial summary
    await update_financial_summary(current_user["_id"], db)
    
    return {"id": str(result.inserted_id), "message": "Transaction created"}

@router.get("/analytics")
async def get_analytics(
    period: str = "monthly",  # daily, weekly, monthly, yearly
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get spending analytics"""
    analytics = await calculate_analytics(current_user["_id"], period, db)
    return analytics

@router.post("/parse-email")
async def parse_email_transactions(
    email_content: str,
    current_user: dict = Depends(get_current_user)
):
    """Parse transactions from email content"""
    transactions = await parse_bank_email(email_content)
    return {"transactions": transactions}
```

### Goal Management Endpoints
```python
# backend/app/api/v1/goals.py
router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])

@router.post("/plan")
async def create_goal_plan(
    goal_request: GoalPlanRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create AI-powered goal plan"""
    # Get user's financial history
    transactions = await get_user_transactions(current_user["_id"], db, months=3)
    
    # Generate AI recommendations
    ai_plan = await generate_goal_plan(
        goal_request,
        transactions,
        current_user["profile"]
    )
    
    return {
        "goal_details": goal_request.dict(),
        "ai_recommendations": ai_plan,
        "saving_strategies": {
            "easy": calculate_easy_strategy(ai_plan),
            "moderate": calculate_moderate_strategy(ai_plan),
            "aggressive": calculate_aggressive_strategy(ai_plan)
        }
    }

@router.post("/create")
async def create_goal(
    goal: GoalCreate,
    strategy: SavingStrategy,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new goal with selected strategy"""
    goal_model = GoalModel(
        user_id=current_user["_id"],
        **goal.dict(),
        saving_strategy=strategy
    )
    
    result = await db.goals.insert_one(goal_model.dict(by_alias=True))
    return {"id": str(result.inserted_id), "message": "Goal created successfully"}

@router.get("/{goal_id}/progress")
async def get_goal_progress(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get goal progress with visualizations"""
    goal = await db.goals.find_one({
        "_id": goal_id,
        "user_id": current_user["_id"]
    })
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    progress = calculate_goal_progress(goal)
    visualization_data = generate_progress_visualization(goal)
    
    return {
        "goal": goal,
        "progress": progress,
        "visualization": visualization_data
    }
```

### Document Upload & RAG Endpoints
```python
# backend/app/api/v1/documents.py
from fastapi import UploadFile, File

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "general",  # general, tax, investment, guide
    current_user: dict = Depends(get_current_user)
):
    """Upload and process documents for RAG"""
    # Save file
    file_path = await save_uploaded_file(file, current_user["_id"])
    
    # Process document
    text_content = await extract_text_from_document(file_path)
    
    # Create embeddings
    embeddings = await create_embeddings(text_content)
    
    # Store in vector database
    doc_id = await store_in_vector_db(
        embeddings,
        text_content,
        {
            "user_id": current_user["_id"],
            "document_type": document_type,
            "filename": file.filename
        }
    )
    
    return {
        "document_id": doc_id,
        "filename": file.filename,
        "chunks_created": len(embeddings)
    }

@router.get("/search")
async def search_documents(
    query: str,
    document_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Search through uploaded documents"""
    results = await search_vector_store(
        query,
        user_id=current_user["_id"],
        document_type=document_type
    )
    return {"results": results}
```

### Chat & AI Endpoints
```python
# backend/app/api/v1/chat.py
router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/message")
async def chat_message(
    message: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Process chat message with RAG"""
    # Get or create session
    session = await get_or_create_session(
        current_user["_id"],
        message.context,
        db
    )
    
    # Retrieve relevant documents
    relevant_docs = await retrieve_relevant_documents(
        message.content,
        message.context,
        current_user["_id"]
    )
    
    # Get user context
    user_context = await get_user_financial_context(current_user["_id"], db)
    
    # Generate response using IBM Granite
    response = await generate_ai_response(
        message.content,
        relevant_docs,
        user_context,
        message.context
    )
    
    # Save to chat history
    await save_chat_interaction(
        session["_id"],
        message.content,
        response,
        relevant_docs,
        db
    )
    
    return {
        "response": response,
        "session_id": session["session_id"],
        "sources": [doc["metadata"] for doc in relevant_docs]
    }

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get chat history for a session"""
    session = await db.chat_sessions.find_one({
        "session_id": session_id,
        "user_id": current_user["_id"]
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"messages": session["messages"]}
```

## 🤖 RAG Pipeline Implementation

```python
# backend/app/ai/rag_pipeline.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class RAGPipeline:
    def __init__(self):
        self.setup_embeddings()
        self.setup_llm()
        self.setup_vector_store()
        
    def setup_embeddings(self):
        """Initialize IBM Granite embeddings"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="ibm-granite/granite-embedding-125m-english",
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def setup_llm(self):
        """Initialize IBM Granite LLM"""
        model_name = "ibm-granite/granite-7b-base"
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_auth_token=os.getenv("HUGGINGFACE_API_KEY")
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            use_auth_token=os.getenv("HUGGINGFACE_API_KEY"),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
    
    def setup_vector_store(self):
        """Initialize ChromaDB vector store"""
        self.vector_store = Chroma(
            persist_directory="./data/embeddings",
            embedding_function=self.embeddings,
            collection_name="finance_documents"
        )
    
    async def process_document(self, text: str, metadata: dict):
        """Process and store document in vector store"""
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        # Create documents with metadata
        documents = [
            {
                "content": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to vector store
        self.vector_store.add_texts(
            texts=[doc["content"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )
        
        return len(documents)
    
    async def retrieve_relevant_documents(
        self,
        query: str,
        context_type: str,
        user_id: str,
        k: int = 5
    ):
        """Retrieve relevant documents for query"""
        # Build filter based on context
        filter_dict = {"user_id": user_id}
        
        if context_type == "tax_advice":
            filter_dict["document_type"] = "tax"
        elif context_type == "investment":
            filter_dict["document_type"] = "investment"
        
        # Retrieve documents
        results = self.vector_store.similarity_search_with_score(
            query,
            k=k,
            filter=filter_dict
        )
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]
    
    async def generate_response(
        self,
        query: str,
        context_documents: list,
        user_context: dict,
        conversation_context: str
    ):
        """Generate AI response using IBM Granite"""
        # Prepare context
        document_context = "\n\n".join([
            f"Document {i+1}: {doc['content']}"
            for i, doc in enumerate(context_documents)
        ])
        
        # Get appropriate system prompt
        system_prompt = self.get_system_prompt(conversation_context)
        
        # Build prompt
        prompt = self.build_prompt(
            system_prompt,
            document_context,
            user_context,
            query
        )
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.95
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        response = response.split("Assistant:")[-1].strip()
        
        return response
    
    def get_system_prompt(self, context: str) -> str:
        """Get appropriate system prompt based on context"""
        prompts = {
            "general": GENERAL_FINANCE_PROMPT,
            "goal_planning": GOAL_PLANNING_PROMPT,
            "tax_advice": TAX_ADVISOR_PROMPT,
            "investment": INVESTMENT_ADVISOR_PROMPT,
            "learning": LEARNING_BOT_PROMPT
        }
        return prompts.get(context, GENERAL_FINANCE_PROMPT)
    
    def build_prompt(
        self,
        system_prompt: str,
        document_context: str,
        user_context: dict,
        query: str
    ) -> str:
        """Build complete prompt for LLM"""
        return f"""
{system_prompt}

### User Financial Context:
Monthly Income: ₹{user_context.get('monthly_income', 'Not provided')}
Monthly Expenses: ₹{user_context.get('monthly_expenses', 'Not provided')}
Savings Rate: {user_context.get('savings_rate', 'Not calculated')}%
Investment Portfolio Value: ₹{user_context.get('total_investments', 0)}
Active Goals: {user_context.get('active_goals_count', 0)}

### Relevant Information:
{document_context}

### User Query:
{query}

### Assistant Response:
"""

# Initialize pipeline
rag_pipeline = RAGPipeline()
```

## 💼 Service Layer Implementation

### Finance Analyzer Service
```python
# backend/app/services/finance_analyzer.py
class FinanceAnalyzerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_pipeline = rag_pipeline
    
    async def analyze_spending_patterns(self, user_id: str, period_days: int = 30):
        """Analyze user's spending patterns"""
        # Get transactions
        start_date = datetime.utcnow() - timedelta(days=period_days)
        transactions = await self.db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": start_date},
            "type": TransactionType.EXPENSE
        }).to_list(None)
        
        # Calculate category-wise spending
        category_spending = {}
        total_spending = 0
        
        for tx in transactions:
            category = tx["category"]
            amount = tx["amount"]
            
            if category not in category_spending:
                category_spending[category] = 0
            
            category_spending[category] += amount
            total_spending += amount
        
        # Calculate percentages
        category_percentages = {
            cat: (amount / total_spending * 100) if total_spending > 0 else 0
            for cat, amount in category_spending.items()
        }
        
        # Identify anomalies
        anomalies = await self.detect_spending_anomalies(transactions)
        
        # Generate AI insights
        insights = await self.generate_spending_insights(
            category_spending,
            category_percentages,
            anomalies
        )
        
        return {
            "total_spending": total_spending,
            "category_breakdown": category_spending,
            "category_percentages": category_percentages,
            "anomalies": anomalies,
            "ai_insights": insights,
            "recommendations": await self.generate_recommendations(insights)
        }
    
    async def detect_spending_anomalies(self, transactions: list):
        """Detect unusual spending patterns"""
        anomalies = []
        
        # Group by category
        category_groups = {}
        for tx in transactions:
            cat = tx["category"]
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(tx["amount"])
        
        # Detect outliers using IQR method
        for category, amounts in category_groups.items():
            if len(amounts) < 4:
                continue
            
            q1 = np.percentile(amounts, 25)
            q3 = np.percentile(amounts, 75)
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
            
            for tx in transactions:
                if tx["category"] == category and tx["amount"] > upper_bound:
                    anomalies.append({
                        "transaction_id": tx["_id"],
                        "category": category,
                        "amount": tx["amount"],
                        "date": tx["date"],
                        "reason": f"Unusually high spending in {category}"
                    })
        
        return anomalies
    
    async def generate_spending_insights(
        self,
        category_spending: dict,
        category_percentages: dict,
        anomalies: list
    ):
        """Generate AI-powered spending insights"""
        prompt = f"""
        Analyze the following spending data and provide actionable insights:
        
        Category Spending:
        {json.dumps(category_spending, indent=2)}
        
        Category Percentages:
        {json.dumps(category_percentages, indent=2)}
        
        Detected Anomalies:
        {json.dumps(anomalies, indent=2)}
        
        Provide:
        1. Key observations about spending patterns
        2. Areas of concern
        3. Opportunities for saving
        4. Comparison with typical spending benchmarks
        """
        
        response = await self.ai_pipeline.generate_response(
            query=prompt,
            context_documents=[],
            user_context={},
            conversation_context="general"
        )
        
        return response
```

### Goal Planner Service
```python
# backend/app/services/goal_planner.py
class GoalPlannerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_pipeline = rag_pipeline
    
    async def generate_goal_plan(
        self,
        goal_request: GoalPlanRequest,
        user_transactions: list,
        user_profile: dict
    ):
        """Generate AI-powered goal plan"""
        # Calculate user's financial capacity
        monthly_income = self.calculate_average_income(user_transactions)
        monthly_expenses = self.calculate_average_expenses(user_transactions)
        available_for_savings = monthly_income - monthly_expenses
        
        # Calculate time to goal
        months_to_goal = self.calculate_months_to_goal(
            goal_request.target_amount,
            goal_request.current_amount,
            available_for_savings
        )
        
        # Generate strategies
        strategies = {
            "easy": self.calculate_easy_strategy(
                goal_request,
                available_for_savings,
                months_to_goal
            ),
            "moderate": self.calculate_moderate_strategy(
                goal_request,
                available_for_savings,
                monthly_expenses,
                months_to_goal
            ),
            "aggressive": self.calculate_aggressive_strategy(
                goal_request,
                available_for_savings,
                monthly_expenses,
                months_to_goal
            )
        }
        
        # Get AI recommendations
        ai_recommendations = await self.get_ai_recommendations(
            goal_request,
            strategies,
            user_profile
        )
        
        return {
            "financial_analysis": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "available_for_savings": available_for_savings
            },
            "strategies": strategies,
            "ai_recommendations": ai_recommendations
        }
    
    def calculate_easy_strategy(self, goal_request, available_savings, months):
        """Calculate easy savings strategy (30% of available)"""
        monthly_saving = available_savings * 0.3
        adjusted_months = goal_request.target_amount / monthly_saving
        
        return {
            "monthly_saving": monthly_saving,
            "time_to_goal": adjusted_months,
            "feasibility": "High",
            "lifestyle_impact": "Minimal",
            "breakdown": {
                "reduce_dining": monthly_saving * 0.4,
                "reduce_shopping": monthly_saving * 0.3,
                "optimize_subscriptions": monthly_saving * 0.3
            }
        }
    
    def calculate_moderate_strategy(self, goal_request, available_savings, expenses, months):
        """Calculate moderate savings strategy (50% of available + 10% expense reduction)"""
        monthly_saving = available_savings * 0.5 + expenses * 0.1
        adjusted_months = goal_request.target_amount / monthly_saving
        
        return {
            "monthly_saving": monthly_saving,
            "time_to_goal": adjusted_months,
            "feasibility": "Medium",
            "lifestyle_impact": "Moderate",
            "breakdown": {
                "from_available": available_savings * 0.5,
                "reduce_dining": expenses * 0.04,
                "reduce_entertainment": expenses * 0.03,
                "reduce_shopping": expenses * 0.03
            }
        }
    
    def calculate_aggressive_strategy(self, goal_request, available_savings, expenses, months):
        """Calculate aggressive savings strategy (80% of available + 20% expense reduction)"""
        monthly_saving = available_savings * 0.8 + expenses * 0.2
        adjusted_months = goal_request.target_amount / monthly_saving
        
        return {
            "monthly_saving": monthly_saving,
            "time_to_goal": adjusted_months,
            "feasibility": "Challenging",
            "lifestyle_impact": "Significant",
            "breakdown": {
                "from_available": available_savings * 0.8,
                "reduce_all_categories": expenses * 0.2
            },
            "additional_income_needed": max(0, goal_request.target_amount / months - monthly_saving)
        }
```

### Tax Advisor Service
```python
# backend/app/services/tax_advisor.py
class TaxAdvisorService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_pipeline = rag_pipeline
    
    async def generate_tax_saving_suggestions(self, user_id: str):
        """Generate personalized tax saving suggestions"""
        # Get user's financial data
        user = await self.db.users.find_one({"_id": user_id})
        income = user["profile"]["annual_income"]
        
        # Get investments
        investments = await self.db.investments.find({"user_id": user_id}).to_list(None)
        
        # Calculate current tax
        current_tax = self.calculate_tax_liability(income, investments)
        
        # Generate suggestions based on sections
        suggestions = {
            "section_80C": await self.get_80c_suggestions(income, investments),
            "section_80D": await self.get_80d_suggestions(user),
            "section_24": await self.get_home_loan_suggestions(user),
            "section_80E": await self.get_education_loan_suggestions(user),
            "section_80TTA": await self.get_savings_interest_suggestions(user)
        }
        
        # Calculate potential savings
        potential_savings = self.calculate_potential_savings(suggestions, current_tax)
        
        # Get AI recommendations
        ai_recommendations = await self.get_tax_ai_recommendations(
            income,
            current_tax,
            suggestions,
            potential_savings
        )
        
        return {
            "current_tax_liability": current_tax,
            "suggestions_by_section": suggestions,
            "potential_savings": potential_savings,
            "ai_recommendations": ai_recommendations,
            "documents_required": self.get_required_documents(suggestions)
        }
    
    async def get_80c_suggestions(self, income: float, investments: list):
        """Get Section 80C suggestions (max 1.5 lakhs)"""
        current_80c = sum([
            inv["amount_invested"]
            for inv in investments
            if inv["type"] in ["ppf", "elss", "life_insurance", "nps"]
        ])
        
        remaining = min(150000 - current_80c, income * 0.15)
        
        suggestions = []
        
        if remaining > 0:
            suggestions.append({
                "instrument": "ELSS Mutual Funds",
                "amount": min(remaining, 50000),
                "lock_in": "3 years",
                "expected_returns": "12-15% p.a.",
                "benefits": "Shortest lock-in, potential for high returns"
            })
            
            suggestions.append({
                "instrument": "PPF",
                "amount": min(remaining, 150000),
                "lock_in": "15 years",
                "expected_returns": "7.1% p.a.",
                "benefits": "Tax-free returns, safe investment"
            })
        
        return {
            "current_investment": current_80c,
            "limit": 150000,
            "remaining": remaining,
            "suggestions": suggestions
        }
    
    def calculate_tax_liability(self, income: float, investments: list):
        """Calculate tax liability based on new tax regime"""
        # Simplified tax calculation
        taxable_income = income
        
        # Apply standard deduction
        taxable_income -= 50000
        
        # Apply investment deductions
        section_80c = sum([
            inv["amount_invested"]
            for inv in investments
            if inv["type"] in ["ppf", "elss", "life_insurance"]
        ])
        taxable_income -= min(section_80c, 150000)
        
        # Calculate tax based on slabs
        tax = 0
        
        if taxable_income <= 250000:
            tax = 0
        elif taxable_income <= 500000:
            tax = (taxable_income - 250000) * 0.05
        elif taxable_income <= 750000:
            tax = 12500 + (taxable_income - 500000) * 0.10
        elif taxable_income <= 1000000:
            tax = 37500 + (taxable_income - 750000) * 0.15
        elif taxable_income <= 1250000:
            tax = 75000 + (taxable_income - 1000000) * 0.20
        elif taxable_income <= 1500000:
            tax = 125000 + (taxable_income - 1250000) * 0.25
        else:
            tax = 187500 + (taxable_income - 1500000) * 0.30
        
        # Add cess
        tax = tax * 1.04
        
        return tax
```

## 🔒 Authentication & Security

```python
# backend/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    
    return user

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 System Prompts & AI Configuration

```python
# backend/app/ai/prompts/finance_prompts.py

GENERAL_FINANCE_PROMPT = """
You are an expert personal finance advisor with deep knowledge of Indian financial systems, tax laws, and investment strategies. Your role is to provide personalized, actionable financial guidance.

Key Guidelines:
1. Always consider the user's risk profile and financial goals
2. Provide specific, actionable advice with concrete numbers
3. Use Indian Rupee (₹) for all monetary values
4. Consider Indian tax laws and investment options
5. Be encouraging but realistic about financial goals
6. Explain complex concepts in simple terms
7. Always prioritize financial security and responsible spending

When providing advice:
- Break down recommendations into clear steps
- Provide multiple options when possible
- Explain the pros and cons of each suggestion
- Include relevant timelines and milestones
- Consider both short-term and long-term impacts
"""

GOAL_PLANNING_PROMPT = """
You are a goal-oriented financial planner specializing in helping users achieve their financial objectives through strategic planning and disciplined saving.

Your approach should:
1. Analyze the user's current financial situation realistically
2. Break down large goals into achievable milestones
3. Provide three distinct strategies: Easy, Moderate, and Aggressive
4. Consider the user's spending patterns and identify areas for optimization
5. Suggest specific expense reduction strategies with amounts
6. Recommend suitable investment options based on the goal timeline
7. Account for inflation and unexpected expenses
8. Provide motivation while being realistic about challenges

Format your response with:
- Clear monthly saving targets
- Specific expense reduction recommendations
- Investment suggestions based on risk profile
- Timeline with milestones
- Potential challenges and solutions
"""

TAX_ADVISOR_PROMPT = """
You are a certified tax consultant specializing in Indian tax laws and optimization strategies for individuals.

Your expertise includes:
1. Current Indian tax slabs and regulations (both old and new regime)
2. All sections for tax deductions (80C, 80D, 24, 80E, etc.)
3. Investment options for tax saving with their benefits and limitations
4. Documentation requirements for tax filing
5. Quarterly tax planning strategies

When providing tax advice:
- Calculate exact tax liability based on provided income
- Identify all applicable deductions and exemptions
- Suggest tax-saving investments with specific amounts
- Explain the lock-in periods and returns
- Provide a month-by-month tax planning calendar
- List required documents for each suggestion
- Compare old vs new tax regime benefits
- Consider the user's age, dependents, and existing investments
"""

INVESTMENT_ADVISOR_PROMPT = """
You are a certified investment advisor with expertise in Indian financial markets and investment instruments.

Your knowledge covers:
1. Equity markets (stocks, mutual funds, ETFs)
2. Debt instruments (FDs, bonds, debt funds)
3. Government schemes (PPF, NSC, SSY, etc.)
4. Gold investments (physical, digital, bonds)
5. Real estate investment options
6. Cryptocurrency regulations in India

Investment principles to follow:
- Assess risk tolerance before recommendations
- Diversification across asset classes
- Age-appropriate asset allocation
- Consider investment horizon and liquidity needs
- Factor in tax implications
- Provide expected returns with risk disclaimers
- Suggest SIP amounts for mutual funds
- Include emergency fund recommendations
"""

LEARNING_BOT_PROMPT = """
You are a friendly financial literacy educator, helping users understand personal finance concepts and build good financial habits.

Your teaching approach:
1. Start with basics and gradually increase complexity
2. Use real-world examples relevant to Indian context
3. Provide analogies to simplify complex concepts
4. Include practical exercises and calculations
5. Share best practices and common pitfalls
6. Recommend learning resources and tools

Topics you can cover:
- Budgeting and expense tracking
- Understanding credit scores and loans
- Investment basics and terminology
- Insurance types and importance
- Tax basics and filing process
- Financial planning for life events
- Retirement planning fundamentals
- Digital payment safety

Always encourage questions and provide patient, detailed explanations.
"""

# Tool calling prompts for specific actions
GOAL_CREATION_TOOL_PROMPT = """
Based on the user's goal details and financial situation, create a structured goal plan.

Extract and structure:
1. Goal name and description
2. Target amount and timeline
3. Recommended monthly contribution
4. Suggested saving strategy (easy/moderate/aggressive)
5. Investment allocation for the goal amount

Return the structured data for goal creation.
"""

TRANSACTION_ANALYSIS_PROMPT = """
Analyze the provided transaction data and identify:
1. Spending patterns and trends
2. Unusual or concerning transactions
3. Category-wise spending efficiency
4. Potential areas for cost reduction
5. Comparison with recommended budget allocations

Provide specific insights with actionable recommendations.
"""
```

## 🚀 Main Application File

```python
# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.config.database import init_db, close_db
from app.api.v1 import auth, users, transactions, goals, investments, chat, documents, analytics
from app.ai.rag_pipeline import rag_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await rag_pipeline.setup()
    print("✅ Database connected")
    print("✅ RAG pipeline initialized")
    yield
    # Shutdown
    await close_db()
    print("👋 Database disconnected")

app = FastAPI(
    title="Personal Finance Bot API",
    description="AI-powered personal finance management system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(goals.router)
app.include_router(investments.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {
        "message": "Personal Finance Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "rag_pipeline": "ready"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## 📚 Requirements File

```python
use uv for as package manager
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.4.2
pydantic[email]==2.4.2

# Database
motor==3.3.2
pymongo==4.5.0
redis==5.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# AI/ML
langchain==0.1.0
langgraph==0.0.20
chromadb==0.4.18
transformers==4.35.2
sentence-transformers==2.2.2
torch==2.1.0
huggingface-hub==0.19.4
tiktoken==0.5.1

# Data Processing
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2

# Email Parsing
beautifulsoup4==4.12.2
python-dateutil==2.8.2

# API Rate Limiting
slowapi==0.1.9

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Utilities
python-multipart==0.0.6
aiofiles==23.2.1
Pillow==10.1.0
```

This completes the comprehensive backend documentation.