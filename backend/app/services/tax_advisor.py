from motor.motor_asyncio import AsyncIOMotorDatabase

class TaxAdvisorService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def generate_tax_saving_suggestions(self, user_id: str):
        """Generate personalized tax saving suggestions"""
        user = await self.db.users.find_one({"_id": user_id})
        if not user or "profile" not in user or "annual_income" not in user["profile"]:
            return {"message": "User profile with annual income not found."}
        
        income = user["profile"]["annual_income"]
        
        investments = await self.db.investments.find({"user_id": user_id}).to_list(None)
        
        current_tax = self.calculate_tax_liability(income, investments)
        
        suggestions = {
            "section_80C": await self.get_80c_suggestions(income, investments),
        }
        
        potential_savings = 0 # Simplified
        
        return {
            "current_tax_liability": current_tax,
            "suggestions_by_section": suggestions,
            "potential_savings": potential_savings,
            "ai_recommendations": "AI recommendations are not yet implemented.",
            "documents_required": []
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
        taxable_income = income
        taxable_income -= 50000
        
        section_80c = sum([
            inv["amount_invested"]
            for inv in investments
            if inv["type"] in ["ppf", "elss", "life_insurance"]
        ])
        taxable_income -= min(section_80c, 150000)
        
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
        
        tax = tax * 1.04
        
        return tax
