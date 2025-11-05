"""
API client for communicating with the backend server.
"""

import requests
from typing import Dict, List, Optional
import streamlit as st


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def _get_headers(self) -> dict:
        """Get headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if "access_token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        return headers

    def login(self, email: str, password: str) -> Optional[Dict]:
        """Login user"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/token",
                data={"username": email, "password": password}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
        return None

    def signup(self, user_data: Dict) -> bool:
        """Register new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Signup failed: {str(e)}")
        return False

    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """Get user transactions"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/transactions",
                headers=self._get_headers(),
                params={"limit": limit}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to fetch transactions: {str(e)}")
        return []

    def create_transaction(self, transaction_data: Dict) -> bool:
        """Create new transaction"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/transactions",
                headers=self._get_headers(),
                json=transaction_data
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Failed to create transaction: {str(e)}")
        return False

    def get_analytics(self, period: str = "monthly") -> Dict:
        """Get spending analytics"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/transactions/analytics",
                headers=self._get_headers(),
                params={"period": period}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to fetch analytics: {str(e)}")
        return {}

    def create_goal_plan(self, goal_data: Dict) -> Dict:
        """Create AI-powered goal plan"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/goals/plan",
                headers=self._get_headers(),
                json=goal_data
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to create goal plan: {str(e)}")
        return {}

    def chat_message(self, message: str, context: str = "general") -> str:
        """Send chat message to AI"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat/message",
                headers=self._get_headers(),
                json={"content": message, "context": context}
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            st.error(f"Chat failed: {str(e)}")
        return "Sorry, I couldn't process your request."
