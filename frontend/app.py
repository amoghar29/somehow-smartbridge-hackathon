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
                if email and password:
                    result = self.api_client.login(email, password)
                    if result and result.get("access_token"):
                        st.session_state.authenticated = True
                        st.session_state.username = email.split('@')[0]
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
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
                    user_data = {"name": name, "email": email, "password": password}
                    success = self.api_client.signup(user_data)
                    if success:
                        st.success("Account created successfully! Please login.")
                    # Error handled in api_client
                else:
                    st.error("Passwords do not match")

    def render_main_content(self):
        st.title("📊 Dashboard")

        # Check backend health
        if not self.api_client.check_health():
            st.error("⚠️ Backend server is not running! Please start the backend server at http://localhost:8000")
            st.info("Run: `cd backend && python main.py` to start the backend")
            return

        st.success("✅ Connected to backend server")
        st.write("Welcome to your financial dashboard powered by AI.")

        # Fetch analytics from backend
        with st.spinner("Loading financial data..."):
            analytics = self.api_client.get_analytics()

        if analytics:
            totals = analytics.get("totals", {})

            # Display key metrics from backend
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                income = totals.get("income", 0)
                st.metric("Monthly Income", f"₹{income:,.0f}")
            with col2:
                expenses = totals.get("expenses", 0)
                st.metric("Monthly Expenses", f"₹{expenses:,.0f}")
            with col3:
                savings = totals.get("savings", 0)
                st.metric("Savings", f"₹{savings:,.0f}")
            with col4:
                savings_rate = totals.get("savings_rate", 0)
                st.metric("Savings Rate", f"{savings_rate:.1f}%")
        else:
            st.warning("Unable to load analytics data")

        st.divider()

        # Recent activity
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📈 Spending Trends")

            if analytics and "trend_data" in analytics:
                trend_data = analytics["trend_data"]
                df = pd.DataFrame(trend_data)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['month'],
                    y=df['income'],
                    mode='lines+markers',
                    name='Income',
                    line=dict(color='#84fab0', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df['month'],
                    y=df['expenses'],
                    mode='lines+markers',
                    name='Expenses',
                    line=dict(color='#f5576c', width=3)
                ))

                fig.update_layout(
                    title='Income vs Expenses Trend',
                    xaxis_title='Month',
                    yaxis_title='Amount (₹)',
                    height=400,
                    hovermode='x unified',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0.02)'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trend data available")

        with col2:
            st.subheader("📋 Recent Transactions")

            # Fetch transactions from backend
            transactions = self.api_client.get_transactions(limit=5)

            if transactions:
                for txn in transactions:
                    desc = txn.get("description", "Unknown")
                    amount = txn.get("amount", 0)
                    txn_type = txn.get("type", "expense")

                    if txn_type == "income":
                        st.write(f"✅ **{desc}**: ₹{amount:,.0f}")
                    else:
                        st.write(f"💸 **{desc}**: ₹{amount:,.0f}")
            else:
                st.info("No transactions yet. Add your first transaction!")

        # Add Transaction Form
        st.divider()
        st.subheader("➕ Add New Transaction")

        with st.form("add_transaction"):
            col1, col2, col3 = st.columns(3)

            with col1:
                description = st.text_input("Description", placeholder="e.g., Grocery Shopping")
            with col2:
                amount = st.number_input("Amount (₹)", min_value=1, value=1000, step=100)
            with col3:
                txn_type = st.selectbox("Type", ["expense", "income"])

            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Salary", "Other"])

            submit = st.form_submit_button("Add Transaction", use_container_width=True)

            if submit and description:
                with st.spinner("Adding transaction..."):
                    result = self.api_client.create_transaction({
                        "description": description,
                        "amount": amount,
                        "category": category,
                        "type": txn_type
                    })

                if result.get("success"):
                    st.success(f"✅ Transaction added successfully! ID: {result.get('transaction_id')}")
                    st.rerun()
                else:
                    st.error(result.get("error", "Failed to add transaction"))

        # AI Assistant Quick Access
        st.divider()
        st.subheader("💡 Ask Your AI Financial Assistant")

        user_question = st.text_input("Ask me anything about personal finance...",
                                     placeholder="e.g., How can I save more money?")

        if st.button("Get AI Advice", use_container_width=True):
            if user_question:
                with st.spinner("🤖 AI is thinking..."):
                    response = self.api_client.get_ai_advice(user_question, persona="professional")
                st.info(f"**AI Response:** {response}")
            else:
                st.warning("Please enter a question")

    def logout(self):
        """Logout user and reset session"""
        self.session.reset()
        st.rerun()


# Run the app
if __name__ == "__main__":
    app = FinanceApp()
    app.run()
