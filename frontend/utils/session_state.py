"""
Session state management for the Streamlit application.
"""

import streamlit as st
from datetime import datetime


class SessionState:
    def __init__(self):
        self.defaults = {
            'authenticated': False,
            'username': None,
            'access_token': None,
            'user_id': None,
            'net_worth': 0,
            'savings_rate': 0,
            'monthly_income': 0,
            'monthly_expenses': 0,
            'active_goals': [],
            'recent_transactions': [],
            'chat_history': [],
            'current_page': 'dashboard',
            'show_transaction_form': False,
            'show_analysis': False,
            'show_ai_chat': False
        }

    def init(self):
        """Initialize session state with defaults"""
        for key, value in self.defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def reset(self):
        """Reset session state to defaults"""
        for key, value in self.defaults.items():
            st.session_state[key] = value

    def update_financial_summary(self, data: dict):
        """Update financial summary in session"""
        st.session_state.net_worth = data.get('net_worth', 0)
        st.session_state.savings_rate = data.get('savings_rate', 0)
        st.session_state.monthly_income = data.get('monthly_income', 0)
        st.session_state.monthly_expenses = data.get('monthly_expenses', 0)

    def add_transaction(self, transaction: dict):
        """Add transaction to recent list"""
        if 'recent_transactions' not in st.session_state:
            st.session_state.recent_transactions = []

        st.session_state.recent_transactions.insert(0, {
            **transaction,
            'timestamp': datetime.now()
        })

        # Keep only last 50 transactions
        st.session_state.recent_transactions = st.session_state.recent_transactions[:50]

    def add_chat_message(self, role: str, content: str):
        """Add message to chat history"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
