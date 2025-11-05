from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class GoalPlannerService:
    """Service for goal planning and strategy generation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def generate_goal_plan(
        self,
        goal_request: Dict,
        user_id: str
    ) -> Dict:
        """Generate comprehensive goal plan with multiple strategies"""
        
        # Get user's financial data
        user = await self.db.users.find_one({"_id": user_id})
        transactions = await self.get_recent_transactions(user_id, months=3)
        
        # Calculate financial capacity
        financial_analysis = await self.analyze_financial_capacity(
            transactions,
            user.get("profile", {})
        )
        
        # Calculate time to goal
        target_date = goal_request["target_date"]
        months_to_goal = self.calculate_months_to_goal(
            datetime.utcnow(),
            target_date
        )
        
        amount_needed = goal_request["target_amount"] - goal_request.get("current_amount", 0)
        
        # Generate strategies
        strategies = {
            "easy": self.calculate_easy_strategy(
                amount_needed,
                months_to_goal,
                financial_analysis
            ),
            "moderate": self.calculate_moderate_strategy(
                amount_needed,
                months_to_goal,
                financial_analysis
            ),
            "aggressive": self.calculate_aggressive_strategy(
                amount_needed,
                months_to_goal,
                financial_analysis
            )
        }
        
        # AI recommendations (simplified version)
        ai_recommendations = self.generate_ai_recommendations(
            goal_request,
            strategies,
            financial_analysis
        )
        
        return {
            "goal_details": {
                "name": goal_request["name"],
                "target_amount": goal_request["target_amount"],
                "current_amount": goal_request.get("current_amount", 0),
                "amount_needed": amount_needed,
                "months_to_goal": months_to_goal,
                "category": goal_request["category"]
            },
            "financial_analysis": financial_analysis,
            "strategies": strategies,
            "ai_recommendations": ai_recommendations
        }
    
    async def get_recent_transactions(self, user_id: str, months: int = 3) -> List[Dict]:
        """Get recent transactions for analysis"""
        start_date = datetime.utcnow() - timedelta(days=30 * months)
        
        transactions = await self.db.transactions.find({
            "user_id": user_id,
            "date": {"$gte": start_date}
        }).to_list(None)
        
        return transactions
    
    async def analyze_financial_capacity(
        self,
        transactions: List[Dict],
        profile: Dict
    ) -> Dict:
        """Analyze user's financial capacity"""
        
        # Calculate monthly averages
        income_txs = [tx for tx in transactions if tx["type"] == "income"]
        expense_txs = [tx for tx in transactions if tx["type"] == "expense"]
        
        total_income = sum(tx["amount"] for tx in income_txs)
        total_expenses = sum(tx["amount"] for tx in expense_txs)
        
        months_count = len(set(tx["date"].month for tx in transactions)) or 1
        
        monthly_income = total_income / months_count
        monthly_expenses = total_expenses / months_count
        available_for_savings = monthly_income - monthly_expenses
        
        # Category-wise breakdown
        category_expenses = {}
        for tx in expense_txs:
            cat = tx["category"]
            if cat not in category_expenses:
                category_expenses[cat] = 0
            category_expenses[cat] += tx["amount"]
        
        # Calculate average for each category
        for cat in category_expenses:
            category_expenses[cat] = category_expenses[cat] / months_count
        
        return {
            "monthly_income": round(monthly_income, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "available_for_savings": round(available_for_savings, 2),
            "savings_rate": round((available_for_savings / monthly_income * 100), 2) if monthly_income > 0 else 0,
            "category_expenses": category_expenses,
            "risk_profile": profile.get("risk_profile", "moderate")
        }
    
    def calculate_months_to_goal(
        self,
        start_date: datetime,
        target_date: datetime
    ) -> int:
        """Calculate months between two dates"""
        delta = target_date - start_date
        return max(1, int(delta.days / 30))
    
    def calculate_easy_strategy(
        self,
        amount_needed: float,
        months_to_goal: int,
        financial_analysis: Dict
    ) -> Dict:
        """
        Easy Strategy: 30% of available savings
        Minimal lifestyle impact
        """
        available = financial_analysis["available_for_savings"]
        monthly_saving = available * 0.30
        
        if monthly_saving <= 0:
            adjusted_months = float('inf')
        else:
            adjusted_months = amount_needed / monthly_saving
        
        # Breakdown of savings sources
        breakdown = {
            "from_available_savings": round(monthly_saving, 2),
            "reduce_dining_out": round(monthly_saving * 0.4, 2),
            "reduce_entertainment": round(monthly_saving * 0.3, 2),
            "optimize_subscriptions": round(monthly_saving * 0.3, 2)
        }
        
        return {
            "monthly_saving": round(monthly_saving, 2),
            "time_to_goal": round(adjusted_months, 1),
            "feasibility": "High - Easy to achieve",
            "lifestyle_impact": "Minimal - Small adjustments only",
            "breakdown": breakdown,
            "additional_income_needed": 0
        }
    
    def calculate_moderate_strategy(
        self,
        amount_needed: float,
        months_to_goal: int,
        financial_analysis: Dict
    ) -> Dict:
        """
        Moderate Strategy: 60% of available + 10% expense reduction
        Moderate lifestyle impact
        """
        available = financial_analysis["available_for_savings"]
        expenses = financial_analysis["monthly_expenses"]
        
        from_savings = available * 0.60
        from_reduction = expenses * 0.10
        monthly_saving = from_savings + from_reduction
        
        if monthly_saving <= 0:
            adjusted_months = float('inf')
        else:
            adjusted_months = amount_needed / monthly_saving
        
        breakdown = {
            "from_available_savings": round(from_savings, 2),
            "reduce_food_expenses": round(expenses * 0.04, 2),
            "reduce_shopping": round(expenses * 0.03, 2),
            "reduce_entertainment": round(expenses * 0.02, 2),
            "optimize_utilities": round(expenses * 0.01, 2)
        }
        
        return {
            "monthly_saving": round(monthly_saving, 2),
            "time_to_goal": round(adjusted_months, 1),
            "feasibility": "Medium - Requires discipline",
            "lifestyle_impact": "Moderate - Noticeable changes",
            "breakdown": breakdown,
            "additional_income_needed": 0
        }
    
    def calculate_aggressive_strategy(
        self,
        amount_needed: float,
        months_to_goal: int,
        financial_analysis: Dict
    ) -> Dict:
        """
        Aggressive Strategy: 90% of available + 20% expense reduction
        Significant lifestyle impact
        """
        available = financial_analysis["available_for_savings"]
        expenses = financial_analysis["monthly_expenses"]
        
        from_savings = available * 0.90
        from_reduction = expenses * 0.20
        monthly_saving = from_savings + from_reduction
        
        if monthly_saving <= 0:
            adjusted_months = float('inf')
        else:
            adjusted_months = amount_needed / monthly_saving
        
        # Check if additional income is needed to meet timeline
        required_monthly = amount_needed / months_to_goal
        additional_needed = max(0, required_monthly - monthly_saving)
        
        breakdown = {
            "from_available_savings": round(from_savings, 2),
            "reduce_all_discretionary": round(from_reduction, 2),
            "eliminate_subscriptions": round(expenses * 0.05, 2),
            "minimize_dining_out": round(expenses * 0.08, 2),
            "reduce_transport": round(expenses * 0.04, 2),
            "other_cuts": round(expenses * 0.03, 2)
        }
        
        return {
            "monthly_saving": round(monthly_saving, 2),
            "time_to_goal": round(adjusted_months, 1),
            "feasibility": "Challenging - Requires significant effort",
            "lifestyle_impact": "Significant - Major changes required",
            "breakdown": breakdown,
            "additional_income_needed": round(additional_needed, 2)
        }
    
    def generate_ai_recommendations(
        self,
        goal_request: Dict,
        strategies: Dict,
        financial_analysis: Dict
    ) -> Dict:
        """Generate AI-powered recommendations"""
        
        amount_needed = goal_request["target_amount"] - goal_request.get("current_amount", 0)
        
        # Determine recommended strategy
        savings_rate = financial_analysis["savings_rate"]
        risk_profile = financial_analysis["risk_profile"]
        
        if savings_rate > 30:
            recommended = "moderate"
        elif savings_rate > 15:
            recommended = "easy"
        else:
            recommended = "aggressive"
        
        # Investment suggestions based on timeline
        target_date = goal_request["target_date"]
        months_to_goal = self.calculate_months_to_goal(datetime.utcnow(), target_date)
        years_to_goal = months_to_goal / 12
        
        if years_to_goal < 1:
            investment_type = "liquid_funds"
            expected_return = "5-6% p.a."
        elif years_to_goal < 3:
            investment_type = "debt_funds"
            expected_return = "7-9% p.a."
        else:
            investment_type = "balanced_funds"
            expected_return = "10-12% p.a."
        
        return {
            "recommended_strategy": recommended,
            "feasibility_score": self.calculate_feasibility_score(
                strategies[recommended],
                financial_analysis
            ),
            "investment_suggestion": {
                "type": investment_type,
                "expected_return": expected_return,
                "risk": "low" if years_to_goal < 1 else "moderate"
            },
            "key_insights": [
                f"You need to save ₹{strategies[recommended]['monthly_saving']:,.0f} per month",
                f"Current savings rate: {savings_rate:.1f}%",
                f"Goal achievable in {strategies[recommended]['time_to_goal']:.1f} months with {recommended} strategy"
            ],
            "tips": self.generate_saving_tips(goal_request["category"], recommended)
        }
    
    def calculate_feasibility_score(
        self,
        strategy: Dict,
        financial_analysis: Dict
    ) -> float:
        """Calculate feasibility score (0-100)"""
        monthly_saving = strategy["monthly_saving"]
        available = financial_analysis["available_for_savings"]
        
        if available <= 0:
            return 0
        
        ratio = monthly_saving / available
        
        if ratio <= 0.3:
            return 95
        elif ratio <= 0.6:
            return 75
        elif ratio <= 0.9:
            return 50
        else:
            return 25
    
    def generate_saving_tips(self, category: str, strategy: str) -> List[str]:
        """Generate category-specific saving tips"""
        
        tips_map = {
            "travel": [
                "Book flights 2-3 months in advance for better deals",
                "Consider off-season travel for significant savings",
                "Use travel rewards credit cards"
            ],
            "education": [
                "Look for scholarships and grants",
                "Consider online courses for skill development",
                "Compare education loan options"
            ],
            "home": [
                "Improve credit score for better loan rates",
                "Save at least 20% for down payment",
                "Research government housing schemes"
            ],
            "emergency": [
                "Automate monthly transfers to emergency fund",
                "Keep in high-yield savings account",
                "Aim for 6 months of expenses"
            ],
            "wedding": [
                "Create detailed budget and stick to it",
                "Consider wedding loans with low interest",
                "Prioritize essential expenses"
            ]
        }
        
        return tips_map.get(category, [
            "Set up automatic transfers on payday",
            "Track all expenses to identify savings opportunities",
            "Review and cut unnecessary subscriptions"
        ])
    
    async def calculate_goal_progress(self, goal: Dict) -> Dict:
        """Calculate detailed goal progress"""
        
        current = goal["current_amount"]
        target = goal["target_amount"]
        progress_percentage = (current / target * 100) if target > 0 else 0
        
        # Calculate time metrics
        start_date = goal["start_date"]
        target_date = goal["target_date"]
        now = datetime.utcnow()
        
        total_days = (target_date - start_date).days
        elapsed_days = (now - start_date).days
        remaining_days = (target_date - now).days
        
        time_progress = (elapsed_days / total_days * 100) if total_days > 0 else 0
        
        # Determine if on track
        on_track = progress_percentage >= time_progress * 0.9  # 90% threshold
        
        # Calculate projected completion
        if current > 0 and elapsed_days > 0:
            daily_rate = current / elapsed_days
            remaining_amount = target - current
            days_to_complete = remaining_amount / daily_rate if daily_rate > 0 else float('inf')
            projected_completion = now + timedelta(days=days_to_complete)
        else:
            projected_completion = None
        
        return {
            "current_amount": current,
            "target_amount": target,
            "progress_percentage": round(progress_percentage, 2),
            "amount_remaining": target - current,
            "time_progress_percentage": round(time_progress, 2),
            "days_elapsed": elapsed_days,
            "days_remaining": max(0, remaining_days),
            "months_remaining": max(0, remaining_days / 30),
            "on_track": on_track,
            "projected_completion": projected_completion,
            "status": "ahead" if progress_percentage > time_progress else "behind" if progress_percentage < time_progress * 0.9 else "on_track"
        }