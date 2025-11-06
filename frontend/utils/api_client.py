"""
API client for communicating with the backend server.
Updated to match FastAPI backend endpoints.
"""

import requests
from typing import Dict, List, Optional
import streamlit as st


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30  # 30 seconds timeout

    def _get_headers(self) -> dict:
        """Get headers for API requests"""
        headers = {"Content-Type": "application/json"}
        return headers

    def check_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_health_status(self) -> Dict:
        """Get detailed health status"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
        return {"status": "unknown"}

    # ========== Transaction Management ==========

    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent transactions from backend"""
        try:
            response = self.session.get(
                f"{self.base_url}/transactions/recent",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("transactions", [])[:limit]
        except Exception as e:
            st.error(f"Failed to fetch transactions: {str(e)}")
        return []

    def create_transaction(self, transaction_data: Dict) -> Dict:
        """Create new transaction"""
        try:
            response = self.session.post(
                f"{self.base_url}/transactions/add",
                headers=self._get_headers(),
                json=transaction_data
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to create transaction: {str(e)}")
        return {"success": False, "error": str(e)}

    # ========== Analytics ==========

    def get_analytics(self) -> Dict:
        """Get financial analytics summary"""
        try:
            response = self.session.get(
                f"{self.base_url}/analytics/summary",
                headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to fetch analytics: {str(e)}")
        return {}

    # ========== AI-Powered Features ==========

    def get_ai_advice(self, question: str, persona: str = "professional") -> str:
        """Get general AI financial advice"""
        try:
            response = self.session.post(
                f"{self.base_url}/ai/generate",
                headers=self._get_headers(),
                json={"question": question, "persona": persona},
                timeout=60  # AI calls can take longer
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response received")
        except requests.exceptions.Timeout:
            return "Request timed out. The AI model might be loading. Please try again in a moment."
        except Exception as e:
            st.error(f"AI request failed: {str(e)}")
            return f"Error: {str(e)}"

    def get_budget_analysis(self, income: float, expenses: Dict[str, float], persona: str = "professional") -> Dict:
        """Get AI-powered budget analysis using /ai/generate endpoint"""
        try:
            # Format expenses as a readable string
            expense_str = ", ".join([f"{k}: ₹{v:,.0f}" for k, v in expenses.items()])
            total_expenses = sum(expenses.values())
            savings = income - total_expenses

            # Create a comprehensive question for the AI
            question = f"""Analyze this monthly budget:

Income: ₹{income:,.0f}
Total Expenses: ₹{total_expenses:,.0f}
Expenses breakdown: {expense_str}
Net Savings: ₹{savings:,.0f}

Please provide:
1. A brief budget summary
2. Key insights about spending patterns
3. Practical recommendations to optimize the budget"""

            # Use /ai/generate endpoint
            response = self.session.post(
                f"{self.base_url}/ai/generate",
                headers=self._get_headers(),
                json={"question": question, "persona": persona},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")

                # Return in expected format
                return {
                    "summary": ai_response,
                    "insights": ai_response
                }
        except requests.exceptions.Timeout:
            st.warning("Request timed out. The AI model might be loading.")
            return {}
        except Exception as e:
            st.error(f"Budget analysis failed: {str(e)}")
        return {}

    def create_goal_plan(self, goal_name: str, target_amount: float, months: int,
                        income: float, persona: str = "professional") -> Dict:
        """Create AI-powered goal plan using /ai/generate endpoint"""
        try:
            monthly_target = target_amount / months if months > 0 else 0

            # Create a comprehensive question for goal planning
            question = f"""Help me plan for this financial goal:

Goal: {goal_name}
Target Amount: ₹{target_amount:,.0f}
Timeline: {months} months
Monthly Income: ₹{income:,.0f}
Required Monthly Savings: ₹{monthly_target:,.0f}

Please provide:
1. A brief analysis of the goal feasibility
2. Step-by-step action plan to achieve this goal
3. Recommended investment strategies based on the timeline
4. Tips for staying on track"""

            # Use /ai/generate endpoint
            response = self.session.post(
                f"{self.base_url}/ai/generate",
                headers=self._get_headers(),
                json={"question": question, "persona": persona},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")

                # Return in expected format
                return {
                    "goal_name": goal_name,
                    "target_amount": target_amount,
                    "months": months,
                    "monthly_savings": monthly_target,
                    "plan": ai_response,
                    "advice": ai_response
                }
        except requests.exceptions.Timeout:
            st.warning("Request timed out. The AI model might be loading.")
            return {}
        except Exception as e:
            st.error(f"Goal planning failed: {str(e)}")
        return {}

    def get_tax_advice(self, income: float, persona: str = "professional") -> str:
        """Get AI-powered tax advice using /ai/generate endpoint"""
        try:
            # Create a comprehensive question for tax planning
            question = f"""Provide tax-saving advice for Indian tax laws:

Annual Income: ₹{income:,.0f}

Please provide:
1. Overview of applicable tax regime (old vs new)
2. Common tax-saving investments under Section 80C
3. Other tax deductions to consider
4. General tax planning tips

Keep it educational and practical. Note: This is general guidance, not professional tax advice."""

            # Use /ai/generate endpoint
            response = self.session.post(
                f"{self.base_url}/ai/generate",
                headers=self._get_headers(),
                json={"question": question, "persona": persona},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No advice available")
        except requests.exceptions.Timeout:
            return "Request timed out. The AI model might be loading. Please try again."
        except Exception as e:
            st.error(f"Tax advice request failed: {str(e)}")
            return f"Error: {str(e)}"

    # ========== Compatibility Methods (for demo) ==========

    def login(self, email: str, password: str) -> Optional[Dict]:
        """
        Simulated login for demo purposes
        Backend doesn't have auth endpoints yet
        """
        if email and password:
            return {
                "access_token": "demo_token",
                "token_type": "bearer",
                "user": {"email": email, "name": email.split('@')[0]}
            }
        return None

    def signup(self, user_data: Dict) -> bool:
        """
        Simulated signup for demo purposes
        Backend doesn't have auth endpoints yet
        """
        return True
