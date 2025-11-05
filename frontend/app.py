"""
Personal Finance Assistant - Main Application
Streamlit-based frontend for financial management and AI-powered insights.
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import APIClient
from utils.session_state import SessionState
from config.settings import BACKEND_URL

# Page configuration
st.set_page_config(
    page_title="Personal Finance Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourrepo/finance-bot',
        'Report a bug': "https://github.com/yourrepo/finance-bot/issues",
        'About': "# Personal Finance Assistant\nAI-powered finance management"
    }
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 0rem;
    }

    /* Cards styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Success alert */
    .success-alert {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin-bottom: 1rem;
    }

    /* Warning alert */
    .warning-alert {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        margin-bottom: 1rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 3rem;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 0.5rem;
        transition: transform 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0.5rem;
        color: #4a5568;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: white;
        color: #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


class FinanceApp:
    def __init__(self):
        self.api_client = APIClient(BACKEND_URL)
        self.session = SessionState()

    def run(self):
        # Initialize session state
        self.session.init()

        # Sidebar for authentication
        self.render_sidebar()

        # Main content area
        if st.session_state.get('authenticated', False):
            self.render_main_content()
        else:
            self.render_login_page()

    def render_sidebar(self):
        with st.sidebar:
            st.title("💰 Finance Assistant")

            if st.session_state.get('authenticated', False):
                st.write(f"Welcome, **{st.session_state.get('username', 'User')}**!")

                # User stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Net Worth", f"₹{st.session_state.get('net_worth', 0):,.0f}")
                with col2:
                    st.metric("Savings Rate", f"{st.session_state.get('savings_rate', 0):.1f}%")

                st.divider()

                # Quick Actions
                st.subheader("Quick Actions")
                if st.button("➕ Add Transaction", use_container_width=True):
                    st.session_state.show_transaction_form = True

                if st.button("📊 Analyze Spending", use_container_width=True):
                    st.session_state.show_analysis = True

                if st.button("💡 Get AI Advice", use_container_width=True):
                    st.session_state.show_ai_chat = True

                st.divider()

                # Settings
                with st.expander("⚙️ Settings"):
                    st.selectbox(
                        "Currency",
                        ["INR (₹)", "USD ($)", "EUR (€)"],
                        key="currency_preference"
                    )

                    st.checkbox("Enable notifications", value=True, key="notifications")
                    st.checkbox("Email alerts", value=True, key="email_alerts")

                st.divider()

                if st.button("🚪 Logout", use_container_width=True):
                    self.logout()
            else:
                st.info("Please login to access your finance dashboard")

    def render_login_page(self):
        st.title("Welcome to Personal Finance Assistant")

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.subheader("Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", use_container_width=True):
                # Simulate login for demo purposes
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.username = email.split('@')[0]
                    st.session_state.net_worth = 500000
                    st.session_state.savings_rate = 25.5
                    st.rerun()
                else:
                    st.error("Please enter both email and password")

        with tab2:
            st.subheader("Create New Account")
            name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

            if st.button("Sign Up", use_container_width=True):
                if password == confirm_password:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Passwords do not match")

    def render_main_content(self):
        st.title("📊 Dashboard")
        st.write("Welcome to your financial dashboard. Navigate using the sidebar to explore different features.")

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Monthly Income", "₹60,000", "+5%")
        with col2:
            st.metric("Monthly Expenses", "₹45,000", "-3%")
        with col3:
            st.metric("Savings", "₹15,000", "+12%")
        with col4:
            st.metric("Goals Progress", "65%", "+8%")

        st.divider()

        # Recent activity
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📈 Spending Trends")
            # Sample data for visualization
            dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
            data = pd.DataFrame({
                'Date': dates,
                'Spending': [2000 + i * 50 for i in range(len(dates))]
            })

            fig = px.line(data, x='Date', y='Spending', title='Daily Spending Pattern')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📋 Recent Transactions")
            transactions = [
                {"desc": "Grocery", "amount": "₹2,500"},
                {"desc": "Electricity Bill", "amount": "₹1,200"},
                {"desc": "Restaurant", "amount": "₹850"},
                {"desc": "Fuel", "amount": "₹3,000"},
                {"desc": "Shopping", "amount": "₹5,500"}
            ]

            for txn in transactions:
                st.write(f"**{txn['desc']}**: {txn['amount']}")

    def logout(self):
        """Logout user and reset session"""
        self.session.reset()
        st.rerun()


# Run the app
if __name__ == "__main__":
    app = FinanceApp()
    app.run()
