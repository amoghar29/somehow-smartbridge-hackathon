Frontend Development Documentation (Streamlit)
Table of Contents
Streamlit Application Structure
Main Application Setup
Dashboard Implementation
Goals Page Implementation
Tax Planner Implementation
Learning Bot Implementation
Components Library
API Client Implementation
Session State Management
Visualization Components
🎨 Streamlit Application Structure
# frontend/app.py
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

# Run the app
if __name__ == "__main__":
    app = FinanceApp()
    app.run()

🎯 Goals Page Complete Implementation
# frontend/pages/2_🎯_Goals.py (continued)
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

def render_goals_page():
    st.title("🎯 Financial Goals")
    
    # Goal creation section
    with st.expander("➕ Create New Goal", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Goal Name", placeholder="e.g., Dream Vacation")
            target_amount = st.number_input("Target Amount (₹)", min_value=1000, value=100000, step=1000)
            current_savings = st.number_input("Current Savings (₹)", min_value=0, value=10000, step=1000)
        
        with col2:
            goal_type = st.selectbox("Goal Type", ["Short Term (<1 year)", "Medium Term (1-3 years)", "Long Term (>3 years)"])
            target_date = st.date_input("Target Date", min_value=datetime.now().date())
            category = st.selectbox("Category", ["Travel", "Education", "Emergency Fund", "Home", "Car", "Retirement", "Other"])
        
        # AI-powered planning
        if st.button("🤖 Get AI Recommendations"):
            with st.spinner("Analyzing your financial situation..."):
                time.sleep(2)  # Simulate API call
                
                st.success("AI Analysis Complete!")
                
                # Display recommendations
                st.markdown("### 📊 AI Recommendations")
                
                tab1, tab2, tab3 = st.tabs(["💚 Easy Plan", "💛 Moderate Plan", "❤️ Aggressive Plan"])
                
                with tab1:
                    st.markdown("""
                    **Easy Savings Plan** (Minimal lifestyle impact)
                    - **Monthly Savings Required**: ₹8,000
                    - **Time to Goal**: 12 months
                    - **Feasibility**: High ✅
                    
                    **How to achieve:**
                    - Reduce dining out by ₹3,200/month
                    - Cut shopping expenses by ₹2,400/month
                    - Optimize subscriptions to save ₹2,400/month
                    """)
                    
                    if st.button("Choose Easy Plan", key="easy_plan"):
                        st.success("Goal created with Easy plan!")
                
                with tab2:
                    st.markdown("""
                    **Moderate Savings Plan** (Some lifestyle adjustments)
                    - **Monthly Savings Required**: ₹12,000
                    - **Time to Goal**: 8 months
                    - **Feasibility**: Medium ⚠️
                    
                    **How to achieve:**
                    - Reduce overall expenses by 10% (₹4,500/month)
                    - Use available savings (₹7,500/month)
                    - Consider part-time income opportunities
                    """)
                    
                    if st.button("Choose Moderate Plan", key="moderate_plan"):
                        st.success("Goal created with Moderate plan!")
                
                with tab3:
                    st.markdown("""
                    **Aggressive Savings Plan** (Significant changes needed)
                    - **Monthly Savings Required**: ₹18,000
                    - **Time to Goal**: 5 months
                    - **Feasibility**: Challenging ❌
                    
                    **How to achieve:**
                    - Cut all non-essential expenses (₹8,000/month)
                    - Use maximum available savings (₹10,000/month)
                    - Additional income required: ₹5,000/month
                    """)
                    
                    if st.button("Choose Aggressive Plan", key="aggressive_plan"):
                        st.success("Goal created with Aggressive plan!")

💰 Tax Planner Implementation
# frontend/pages/3_💰_Tax_Planner.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_tax_planner():
    st.title("💰 Tax Planning Assistant")
    
    # Tax calculation section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Income Details")
        
        annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, value=1200000, step=10000)
        
        # Deductions input
        st.subheader("📉 Deductions")
        
        tab1, tab2, tab3 = st.tabs(["Section 80C", "Section 80D", "Other Deductions"])
        
        with tab1:
            st.markdown("**Section 80C - Maximum ₹1,50,000**")
            ppf = st.number_input("PPF Investment", min_value=0, max_value=150000, value=50000)
            elss = st.number_input("ELSS Mutual Funds", min_value=0, max_value=150000, value=30000)
            life_insurance = st.number_input("Life Insurance Premium", min_value=0, max_value=150000, value=20000)
            tuition_fees = st.number_input("Children's Tuition Fees", min_value=0, max_value=150000, value=0)
            
            total_80c = min(ppf + elss + life_insurance + tuition_fees, 150000)
            st.metric("Total 80C Deductions", f"₹{total_80c:,}")
        
        with tab2:
            st.markdown("**Section 80D - Medical Insurance**")
            health_insurance_self = st.number_input("Health Insurance (Self & Family)", min_value=0, max_value=25000, value=15000)
            health_insurance_parents = st.number_input("Health Insurance (Parents)", min_value=0, max_value=50000, value=20000)
            
            total_80d = health_insurance_self + health_insurance_parents
            st.metric("Total 80D Deductions", f"₹{total_80d:,}")
        
        with tab3:
            st.markdown("**Other Deductions**")
            home_loan_interest = st.number_input("Home Loan Interest (Section 24)", min_value=0, max_value=200000, value=0)
            education_loan = st.number_input("Education Loan Interest (Section 80E)", min_value=0, value=0)
            nps = st.number_input("NPS Contribution (Section 80CCD)", min_value=0, max_value=50000, value=0)
            
            total_other = home_loan_interest + education_loan + nps
            st.metric("Other Deductions", f"₹{total_other:,}")
    
    with col2:
        st.subheader("📊 Tax Calculation")
        
        # Tax calculation
        total_deductions = total_80c + total_80d + total_other + 50000  # Standard deduction
        taxable_income = max(annual_income - total_deductions, 0)
        
        # Calculate tax (simplified new regime)
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
        tax_with_cess = tax * 1.04
        
        # Display metrics
        st.metric("Gross Income", f"₹{annual_income:,}")
        st.metric("Total Deductions", f"₹{total_deductions:,}")
        st.metric("Taxable Income", f"₹{taxable_income:,}")
        st.metric("Tax Payable", f"₹{tax_with_cess:,.0f}", f"-₹{(annual_income * 0.3 - tax_with_cess):,.0f} saved")
        
        # Effective tax rate
        effective_rate = (tax_with_cess / annual_income * 100) if annual_income > 0 else 0
        st.metric("Effective Tax Rate", f"{effective_rate:.1f}%")
    
    st.divider()
    
    # AI Tax Suggestions
    st.subheader("🤖 AI Tax-Saving Suggestions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📈 Investment Suggestions**
        - Increase ELSS investment by ₹40,000
        - Start NPS with ₹50,000/year
        - Consider PPF for long-term savings
        
        **Potential Saving**: ₹28,000
        """)
    
    with col2:
        st.markdown("""
        **🏠 Property Benefits**
        - Claim HRA if paying rent
        - Consider home loan for Section 24
        - Register joint ownership for benefits
        
        **Potential Saving**: ₹45,000
        """)
    
    with col3:
        st.markdown("""
        **👨‍👩‍👧‍👦 Family Planning**
        - Health insurance for parents
        - Education expenses for children
        - Dependent disability benefits
        
        **Potential Saving**: ₹15,000
        """)
    
    # Tax comparison chart
    st.subheader("📊 Old vs New Tax Regime Comparison")
    
    regime_data = pd.DataFrame({
        'Income Slab': ['0-2.5L', '2.5-5L', '5-7.5L', '7.5-10L', '10-12.5L', '12.5-15L', '>15L'],
        'Old Regime': [0, 5, 20, 20, 30, 30, 30],
        'New Regime': [0, 5, 10, 15, 20, 25, 30]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Old Regime', x=regime_data['Income Slab'], y=regime_data['Old Regime']))
    fig.add_trace(go.Bar(name='New Regime', x=regime_data['Income Slab'], y=regime_data['New Regime']))
    
    fig.update_layout(
        barmode='group',
        height=300,
        xaxis_title="Income Slab",
        yaxis_title="Tax Rate (%)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Documents checklist
    with st.expander("📄 Documents Required for Tax Filing"):
        st.markdown("""
        **Income Documents:**
        - [ ] Form 16 from employer
        - [ ] Form 26AS (Tax Credit Statement)
        - [ ] Salary slips
        - [ ] Bank statements
        
        **Investment Proofs:**
        - [ ] PPF passbook/statements
        - [ ] ELSS investment receipts
        - [ ] Life insurance premium receipts
        - [ ] NPS contribution certificate
        
        **Deduction Proofs:**
        - [ ] Health insurance premium receipts
        - [ ] Home loan interest certificate
        - [ ] Education loan interest certificate
        - [ ] Rent receipts/agreement (for HRA)
        """)

🤖 AI Assistant/Learning Bot Implementation
# frontend/pages/4_🤖_AI_Assistant.py
import streamlit as st
from datetime import datetime

def render_ai_assistant():
    st.title("🤖 AI Financial Assistant")
    
    # Chat interface
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Learning Center", "❓ FAQs"])
    
    with tab1:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your personal finance assistant. How can I help you today?"}
            ]
        
        # Chat context selector
        col1, col2 = st.columns([3, 1])
        with col1:
            context = st.selectbox(
                "Select Context",
                ["General Finance", "Goal Planning", "Tax Advice", "Investment", "Learning"],
                key="chat_context"
            )
        with col2:
            if st.button("Clear Chat"):
                st.session_state.messages = [
                    {"role": "assistant", "content": "Chat cleared. How can I help you?"}
                ]
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about your finances..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate AI response (simulated)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Simulated AI response based on context
                    if "tax" in prompt.lower():
                        response = """Based on your income profile, here are some tax-saving suggestions:

1. **Maximize Section 80C** (₹1.5 lakhs limit):
   - Consider ELSS mutual funds for better returns
   - PPF for guaranteed tax-free returns
   
2. **Health Insurance (Section 80D)**:
   - You can claim up to ₹25,000 for self and family
   - Additional ₹50,000 for parents (senior citizens)

3. **NPS Contribution**:
   - Extra ₹50,000 deduction under Section 80CCD(1B)
   
Would you like me to calculate your potential tax savings?"""
                    
                    elif "goal" in prompt.lower():
                        response = """I can help you plan your financial goals! Based on your current savings rate of 25%, here's what I suggest:

**For your Emergency Fund goal:**
- Target: ₹3,00,000 (6 months of expenses)
- Current: ₹1,80,000 (60% complete)
- Monthly contribution needed: ₹15,000
- Timeline: 8 months to completion

**Tips to accelerate:**
1. Reduce dining expenses by 20% (save ₹2,000/month)
2. Optimize subscriptions (save ₹1,500/month)
3. Consider a side hustle for extra income

Shall I create a detailed savings plan for you?"""
                    
                    elif "invest" in prompt.lower():
                        response = """Based on your moderate risk profile, here's a balanced investment strategy:

**Recommended Asset Allocation:**
- **Equity (50%)**: ₹2,70,000
  - Large Cap Funds: 30%
  - Mid Cap Funds: 15%
  - International Funds: 5%
  
- **Debt (30%)**: ₹1,62,000
  - Corporate Bonds: 15%
  - Government Securities: 15%
  
- **Gold (10%)**: ₹54,000
  - Sovereign Gold Bonds
  
- **Emergency Fund (10%)**: ₹54,000
  - Liquid Funds

Your current portfolio seems overweight in equity. Consider rebalancing for better risk management.

Would you like specific fund recommendations?"""
                    
                    else:
                        response = f"""I understand you're asking about {prompt}. Let me help you with that.

Based on your financial profile:
- Monthly Income: ₹60,000
- Monthly Expenses: ₹45,000
- Savings Rate: 25%

Here's my analysis and suggestions:

1. You're doing well with a 25% savings rate
2. Consider automating your savings
3. Review and optimize your expenses monthly
4. Set up specific goals for better planning

Is there anything specific you'd like to explore?"""
                    
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        st.subheader("📚 Financial Learning Center")
        
        # Learning categories
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📈 Investment Basics**
            - What are Mutual Funds?
            - Understanding Stock Markets
            - Bond Investment Guide
            - Portfolio Diversification
            - Risk vs Returns
            """)
            if st.button("Start Learning →", key="invest_learn"):
                st.info("Loading investment course...")
        
        with col2:
            st.markdown("""
            **💰 Tax Planning**
            - Income Tax Basics
            - Deductions & Exemptions
            - Tax-saving Instruments
            - ITR Filing Guide
            - Advance Tax Planning
            """)
            if st.button("Start Learning →", key="tax_learn"):
                st.info("Loading tax planning course...")
        
        with col3:
            st.markdown("""
            **🎯 Financial Planning**
            - Budgeting 101
            - Emergency Fund Setup
            - Goal-based Investing
            - Retirement Planning
            - Insurance Planning
            """)
            if st.button("Start Learning →", key="plan_learn"):
                st.info("Loading financial planning course...")
        
        # Interactive quiz
        st.divider()
        st.subheader("🎮 Test Your Knowledge")
        
        with st.expander("Take a Quick Quiz"):
            q1 = st.radio(
                "What is the maximum deduction under Section 80C?",
                ["₹1,00,000", "₹1,50,000", "₹2,00,000", "₹2,50,000"]
            )
            
            q2 = st.radio(
                "Which investment has the shortest lock-in period for tax saving?",
                ["PPF", "ELSS", "NSC", "Tax Saver FD"]
            )
            
            if st.button("Submit Quiz"):
                score = 0
                if q1 == "₹1,50,000":
                    score += 1
                if q2 == "ELSS":
                    score += 1
                
                st.success(f"Your score: {score}/2")
                if score == 2:
                    st.balloons()
    
    with tab3:
        st.subheader("❓ Frequently Asked Questions")
        
        faqs = [
            {
                "question": "How much should I save monthly?",
                "answer": "A good rule of thumb is the 50-30-20 rule: 50% for needs, 30% for wants, and 20% for savings. However, aim for at least 20-30% savings rate for better financial security."
            },
            {
                "question": "What is an emergency fund?",
                "answer": "An emergency fund is 3-6 months of expenses saved for unexpected situations like job loss or medical emergencies. Keep it in liquid instruments like savings accounts or liquid funds."
            },
            {
                "question": "ELSS vs PPF - Which is better?",
                "answer": "ELSS offers potentially higher returns (12-15%) with 3-year lock-in, while PPF provides guaranteed returns (7.1%) with 15-year lock-in. Choose based on your risk appetite and liquidity needs."
            },
            {
                "question": "How to improve credit score?",
                "answer": "Pay bills on time, maintain low credit utilization (<30%), avoid multiple loan applications, maintain old credit accounts, and regularly check your credit report for errors."
            }
        ]
        
        for faq in faqs:
            with st.expander(faq["question"]):
                st.write(faq["answer"])

🧩 Components Library
# frontend/components/charts.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_spending_chart(data: pd.DataFrame, chart_type: str = "line"):
    """Create spending trend chart"""
    if chart_type == "line":
        fig = go.Figure()
        for column in data.columns[1:]:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data[column],
                mode='lines+markers',
                name=column
            ))
    elif chart_type == "bar":
        fig = go.Figure(data=[
            go.Bar(x=data['Category'], y=data['Amount'])
        ])
    
    fig.update_layout(
        height=400,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )
    
    return fig

def create_portfolio_pie(portfolio_data: dict):
    """Create portfolio allocation pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=list(portfolio_data.keys()),
        values=list(portfolio_data.values()),
        hole=0.3
    )])
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_goal_progress_gauge(current: float, target: float):
    """Create goal progress gauge chart"""
    percentage = (current / target) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Goal Progress"},
        delta={'reference': 50},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 25], 'color': "lightgray"},
                   {'range': [25, 50], 'color': "gray"},
                   {'range': [50, 75], 'color': "lightblue"},
                   {'range': [75, 100], 'color': "blue"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}}
    ))
    
    return fig

# frontend/components/cards.py
import streamlit as st

def metric_card(title: str, value: str, delta: str = None, color: str = "blue"):
    """Create a custom metric card"""
    colors = {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "green": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)",
        "red": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "yellow": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    }
    
    background = colors.get(color, colors["blue"])
    
    html = f"""
    <div style="
        background: {background};
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h4 style="margin:0;">{title}</h4>
        <h2 style="margin:0.5rem 0;">{value}</h2>
        {f'<p style="margin:0;opacity:0.8;">{delta}</p>' if delta else ''}
    </div>
    """
    
    return st.markdown(html, unsafe_allow_html=True)

def summary_card(title: str, items: list):
    """Create a summary card with list items"""
    items_html = "".join([f"<li>{item}</li>" for item in items])
    
    html = f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h4 style="margin:0 0 1rem 0;">{title}</h4>
        <ul style="margin:0;padding-left:1.5rem;">
            {items_html}
        </ul>
    </div>
    """
    
    return st.markdown(html, unsafe_allow_html=True)

🔗 API Client Implementation
# frontend/utils/api_client.py
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

💾 Session State Management
# frontend/utils/session_state.py
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

📋 Frontend Requirements
# frontend/requirements.txt
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.3
numpy==1.24.3
requests==2.31.0
python-dateutil==2.8.2

🚀 Running the Frontend
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# For development with hot reload
streamlit run app.py --server.runOnSave true

🎨 UI/UX Best Practices
Responsive Design: Use Streamlit's column layout for responsive design
Loading States: Always show spinners for API calls
Error Handling: Display user-friendly error messages
Data Caching: Use @st.cache_data for expensive computations
Session Management: Properly manage user sessions and auth tokens
Visual Feedback: Use success/error messages for user actions
Progressive Disclosure: Use expanders for advanced options
Consistent Theming: Maintain consistent colors and styling
📱 Mobile Responsiveness
The Streamlit app automatically adapts to mobile screens, but consider:
Using single column layouts for critical information
Minimizing sidebar usage on mobile
Testing on various screen sizes
Providing touch-friendly interaction elements
This completes the comprehensive frontend documentation for your Personal Finance RAG Chatbot using Streamlit.

