"""
Budget Analysis Page - AI-powered budget insights
"""

import streamlit as st
from utils.api_client import APIClient
from config.settings import BACKEND_URL
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Budget Analysis", page_icon="💰", layout="wide")

# Initialize API client
api_client = APIClient(BACKEND_URL)

st.title("💰 Budget Analysis")

# Check backend connection
if not api_client.check_health():
    st.error("⚠️ Backend server is not running! Please start it at http://localhost:8000")
    st.stop()

st.write("Analyze your spending patterns and get AI-powered insights to optimize your budget.")

# Budget input section
st.subheader("📝 Enter Your Budget Details")

col1, col2 = st.columns([1, 2])

with col1:
    monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=5000)
    persona = st.selectbox("Financial Profile", ["conservative", "professional", "aggressive"])

with col2:
    st.markdown("**Monthly Expenses by Category:**")

    col_a, col_b = st.columns(2)

    with col_a:
        housing = st.number_input("Housing", min_value=0, value=15000, step=1000)
        food = st.number_input("Food & Dining", min_value=0, value=10000, step=500)
        transport = st.number_input("Transportation", min_value=0, value=5000, step=500)

    with col_b:
        entertainment = st.number_input("Entertainment", min_value=0, value=3000, step=500)
        shopping = st.number_input("Shopping", min_value=0, value=5000, step=500)
        other = st.number_input("Other", min_value=0, value=2000, step=500)

expenses = {
    "Housing": housing,
    "Food": food,
    "Transportation": transport,
    "Entertainment": entertainment,
    "Shopping": shopping,
    "Other": other
}

total_expenses = sum(expenses.values())
savings = monthly_income - total_expenses

# Quick metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Income", f"₹{monthly_income:,.0f}")
with col2:
    st.metric("Total Expenses", f"₹{total_expenses:,.0f}")
with col3:
    st.metric("Net Savings", f"₹{savings:,.0f}", delta=f"{(savings/monthly_income*100):.1f}%" if monthly_income > 0 else "0%")
with col4:
    savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0
    st.metric("Savings Rate", f"{savings_rate:.1f}%")

if st.button("🤖 Get AI Budget Analysis", use_container_width=True, type="primary"):
    st.divider()
    st.subheader("🤖 AI Budget Analysis & Insights")

    with st.spinner("AI is analyzing your budget..."):
        # Call backend AI budget analysis
        result = api_client.get_budget_analysis(
            income=monthly_income,
            expenses=expenses,
            persona=persona
        )

    if result:
        # Display summary
        if "summary" in result:
            st.success("✅ Analysis Complete!")
            st.markdown(f"**Budget Summary:**\n\n{result['summary']}")

        # Display insights
        if "insights" in result:
            st.info(f"**💡 AI Insights & Recommendations:**\n\n{result['insights']}")
    else:
        st.error("Failed to get budget analysis. Please try again.")

# Expense breakdown visualization
st.divider()
st.subheader("📊 Expense Breakdown")

col1, col2 = st.columns(2)

with col1:
    # Pie chart
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(expenses.keys()),
        values=list(expenses.values()),
        hole=0.4,
        marker=dict(colors=['#667eea', '#764ba2', '#84fab0', '#8fd3f4', '#f093fb', '#feca57'])
    )])

    fig_pie.update_layout(
        title="Expense Distribution",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Bar chart
    fig_bar = go.Figure(data=[
        go.Bar(
            x=list(expenses.keys()),
            y=list(expenses.values()),
            marker_color='#667eea'
        )
    ])

    fig_bar.update_layout(
        title="Expenses by Category",
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# Budgeting tips
st.divider()
st.subheader("💡 Budgeting Best Practices")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 50-30-20 Rule**
    - 50% Needs (housing, food)
    - 30% Wants (entertainment)
    - 20% Savings & Investments
    """)

with col2:
    st.markdown("""
    **💸 Reduce Expenses**
    - Track daily spending
    - Cut subscriptions
    - Cook at home more
    - Use public transport
    - Avoid impulse buying
    """)

with col3:
    st.markdown("""
    **📈 Increase Savings**
    - Automate savings
    - Set specific goals
    - Emergency fund first
    - Invest surplus wisely
    - Review monthly
    """)

# Category recommendations
expense_percentages = {k: (v/monthly_income*100) if monthly_income > 0 else 0 for k, v in expenses.items()}

st.divider()
st.subheader("⚠️ Category Analysis")

for category, percentage in expense_percentages.items():
    if percentage > 30:
        st.warning(f"**{category}**: {percentage:.1f}% of income - Consider reducing this expense")
    elif percentage > 20:
        st.info(f"**{category}**: {percentage:.1f}% of income - Monitor this expense")
    else:
        st.success(f"**{category}**: {percentage:.1f}% of income - Good control")
