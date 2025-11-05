"""RAG Pipeline using IBM Granite models"""

import os
from typing import List, Dict, Optional
import torch
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

from app.config.settings import settings
from app.ai.prompts.finance_prompts import get_system_prompt, build_contextualized_prompt

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG Pipeline for document retrieval and AI response generation"""
    
    def __init__(self):
        self.embeddings_model = None
        self.vector_store = None
        self.text_splitter = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialized = False
    
    async def initialize(self):
        """Initialize RAG components"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Initialize embeddings model
            self._setup_embeddings()
            
            # Initialize vector store
            self._setup_vector_store()
            
            # Initialize text splitter
            self._setup_text_splitter()
            
            self._initialized = True
            logger.info(f"✅ RAG pipeline initialized successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    
    def _setup_embeddings(self):
        """Setup embeddings model"""
        try:
            # Using sentence-transformers for embeddings
            # You can switch to IBM Granite embeddings when available
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            logger.info(f"Loading embeddings model: {model_name}")
            self.embeddings_model = SentenceTransformer(model_name, device=self.device)
            logger.info("✅ Embeddings model loaded")
            
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            # Fallback to a smaller model
            logger.info("Trying fallback model...")
            self.embeddings_model = SentenceTransformer(
                "paraphrase-MiniLM-L3-v2",
                device=self.device
            )
    
    def _setup_vector_store(self):
        """Setup ChromaDB vector store"""
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.Client(Settings(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Finance documents and knowledge base"}
            )
            
            logger.info("✅ Vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _setup_text_splitter(self):
        """Setup text splitter for chunking"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        if not self._initialized:
            raise RuntimeError("RAG pipeline not initialized. Call initialize() first.")
        
        embeddings = self.embeddings_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        return embeddings.tolist()
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> int:
        """Add documents to vector store"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create chunks
            all_chunks = []
            all_metadatas = []
            all_ids = []
            
            for i, (text, metadata) in enumerate(zip(texts, metadatas)):
                chunks = self.text_splitter.split_text(text)
                
                for j, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = j
                    chunk_metadata["total_chunks"] = len(chunks)
                    all_metadatas.append(chunk_metadata)
                    
                    # Generate ID if not provided
                    chunk_id = f"{ids[i] if ids else i}_{j}" if ids else f"doc_{i}_chunk_{j}"
                    all_ids.append(chunk_id)
            
            # Create embeddings
            embeddings = self.create_embeddings(all_chunks)
            
            # Add to vector store
            self.collection.add(
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            logger.info(f"Added {len(all_chunks)} chunks to vector store")
            return len(all_chunks)
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def search_documents(
        self,
        query: str,
        user_id: str,
        context_type: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Search for relevant documents"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create query embedding
            query_embedding = self.create_embeddings([query])[0]
            
            # Build filter
            where_filter = {"user_id": user_id}
            if context_type:
                where_filter["context_type"] = context_type
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            documents = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    async def generate_response(
        self,
        query: str,
        user_context: Dict,
        context_type: str = "general",
        retrieved_docs: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate AI response using retrieved context
        
        Note: This is a simplified version. In production, you would use:
        - IBM Granite LLM via API or local deployment
        - OpenAI API as fallback
        - Or any other LLM of your choice
        """
        
        # Get system prompt
        system_prompt = get_system_prompt(context_type)
        
        # Build contextualized prompt
        prompt = build_contextualized_prompt(
            system_prompt,
            user_context,
            retrieved_docs or [],
            query
        )
        
        # In production, you would call your LLM here
        # For now, returning a placeholder response
        
        # Example using OpenAI (if you have the key)
        if settings.OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
        
        # Fallback response
        return self._generate_fallback_response(query, context_type, user_context)
    
    def _generate_fallback_response(
        self,
        query: str,
        context_type: str,
        user_context: Dict
    ) -> str:
        """Generate a fallback response when LLM is not available"""
        
        income = user_context.get('monthly_income', 0)
        expenses = user_context.get('monthly_expenses', 0)
        savings = income - expenses
        savings_rate = user_context.get('savings_rate', 0)
        
        if context_type == "goal_planning":
            return f"""Based on your financial profile:
            
**Current Situation:**
- Monthly Income: ₹{income:,.0f}
- Monthly Expenses: ₹{expenses:,.0f}
- Available for Savings: ₹{savings:,.0f}
- Savings Rate: {savings_rate:.1f}%

**Recommendations:**
1. Start with automating your savings - set up auto-transfer on salary day
2. Aim to increase your savings rate to at least 20%
3. Consider reducing discretionary expenses by 10-15%
4. Build an emergency fund of 6 months expenses (₹{expenses * 6:,.0f})

Would you like me to create a detailed savings plan for a specific goal?"""
        
        elif context_type == "investment":
            return f"""Investment Strategy for Your Profile:

**Asset Allocation Recommendation:**
- Equity: 60% (for growth)
- Debt: 30% (for stability)
- Gold: 5% (hedge)
- Cash/Liquid: 5% (emergencies)

**Suggested Investment Options:**
1. **Equity Mutual Funds (SIP):** ₹{int(savings * 0.4):,}/month
   - Large Cap Index Funds
   - Flexi Cap Funds
   
2. **Debt Investments:** ₹{int(savings * 0.3):,}/month
   - PPF (for tax benefits)
   - Corporate Bonds
   
3. **Gold:** ₹{int(savings * 0.1):,}/month
   - Sovereign Gold Bonds
   
4. **Emergency Fund:** ₹{int(savings * 0.2):,}/month
   - High-yield savings account

Remember: Diversification is key to managing risk!"""
        
        else:
            return f"""Thank you for your question! Here's what I can help you with:

**Your Financial Overview:**
- Monthly Income: ₹{income:,.0f}
- Monthly Expenses: ₹{expenses:,.0f}
- Savings Potential: ₹{savings:,.0f}
- Current Savings Rate: {savings_rate:.1f}%

**I can help you with:**
1. Creating and tracking financial goals
2. Investment planning and recommendations
3. Tax optimization strategies
4. Spending analysis and budgeting
5. Retirement planning

Please let me know which area you'd like to explore, and I'll provide detailed guidance!

*Note: For personalized advice, consider consulting with a certified financial advisor.*"""
    
    async def process_document_upload(
        self,
        content: str,
        metadata: Dict
    ) -> int:
        """Process uploaded document and add to vector store"""
        if not self._initialized:
            await self.initialize()
        
        # Add single document
        chunks = await self.add_documents(
            texts=[content],
            metadatas=[metadata],
            ids=[metadata.get("document_id", "doc_" + str(hash(content)))]
        )
        
        return chunks


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()


async def get_rag_pipeline() -> RAGPipeline:
    """Get initialized RAG pipeline"""
    if not rag_pipeline._initialized:
        await rag_pipeline.initialize()
    return rag_pipeline