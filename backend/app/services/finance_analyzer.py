from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import numpy as np
import json

from app.ai.rag_pipeline import rag_pipeline
from app.models.transaction import TransactionType

class FinanceAnalyzerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_pipeline = rag_pipeline
    
    async def analyze_spending_patterns(self, user_id: str, period_days: int = 30):
        """Analyze user's spending patterns"""
        start_date = datetime.utcnow() - timedelta(days=period_days)
        transactions = await self.db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": start_date},
            "type": TransactionType.EXPENSE
        }).to_list(None)
        
        category_spending = {}
        total_spending = 0
        
        for tx in transactions:
            category = tx["category"]
            amount = tx["amount"]
            
            if category not in category_spending:
                category_spending[category] = 0
            
            category_spending[category] += amount
            total_spending += amount
        
        category_percentages = {
            cat: (amount / total_spending * 100) if total_spending > 0 else 0
            for cat, amount in category_spending.items()
        }
        
        anomalies = await self.detect_spending_anomalies(transactions)
        
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
        
        category_groups = {}
        for tx in transactions:
            cat = tx["category"]
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(tx["amount"])
        
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
                        "transaction_id": str(tx["_id"]),
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
        {json.dumps(anomalies, indent=2, default=str)}
        
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

    async def generate_recommendations(self, insights: str):
        """Generate recommendations based on AI insights"""
        # This is a placeholder. In a real app, you would parse the insights
        # and generate structured recommendations.
        return ["Reduce spending on dining out", "Cancel unused subscriptions"]
