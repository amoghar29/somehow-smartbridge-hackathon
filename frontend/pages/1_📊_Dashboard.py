"""
Dashboard page - Overview of financial status and recent activity.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Financial Dashboard")

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login to view your dashboard")
    st.stop()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Monthly Income", "₹60,000", "+5%")
with col2:
    st.metric("Monthly Expenses", "₹45,000", "-3%")
with col3:
    st.metric("Net Savings", "₹15,000", "+12%")
with col4:
    st.metric("Savings Rate", "25%", "+2%")

st.divider()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Monthly Spending Trends")

    # Sample spending data
    categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare']
    amounts = [12000, 8000, 10000, 7000, 5000, 3000]

    fig = go.Figure(data=[
        go.Bar(x=categories, y=amounts, marker_color='#667eea')
    ])

    fig.update_layout(
        height=300,
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Spending over time
    st.subheader("📉 Daily Spending Pattern")

    dates = pd.date_range(start='2024-11-01', end='2024-11-05', freq='D')
    daily_spending = pd.DataFrame({
        'Date': dates,
        'Amount': [1500, 2000, 1200, 1800, 2200]
    })

    fig2 = px.line(daily_spending, x='Date', y='Amount', markers=True)
    fig2.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )

    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("📋 Recent Transactions")

    transactions = [
        {"date": "Nov 5", "desc": "Grocery Store", "amount": -2500, "category": "Food"},
        {"date": "Nov 4", "desc": "Salary Credit", "amount": 60000, "category": "Income"},
        {"date": "Nov 4", "desc": "Electricity Bill", "amount": -1200, "category": "Bills"},
        {"date": "Nov 3", "desc": "Restaurant", "amount": -850, "category": "Food"},
        {"date": "Nov 3", "desc": "Fuel", "amount": -3000, "category": "Transport"},
        {"date": "Nov 2", "desc": "Shopping Mall", "amount": -5500, "category": "Shopping"},
        {"date": "Nov 1", "desc": "Movie Tickets", "amount": -600, "category": "Entertainment"}
    ]

    for txn in transactions:
        color = "green" if txn["amount"] > 0 else "red"
        sign = "+" if txn["amount"] > 0 else ""
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**{txn['desc']}**")
                st.caption(f"{txn['date']} • {txn['category']}")
            with col_b:
                st.markdown(f"<p style='color:{color};text-align:right;font-weight:bold;'>{sign}₹{abs(txn['amount']):,}</p>", unsafe_allow_html=True)
            st.divider()

    st.subheader("🎯 Active Goals")

    goals = [
        {"name": "Emergency Fund", "progress": 60, "target": "₹3,00,000"},
        {"name": "Vacation", "progress": 35, "target": "₹1,50,000"},
        {"name": "New Laptop", "progress": 80, "target": "₹80,000"}
    ]

    for goal in goals:
        st.write(f"**{goal['name']}** ({goal['progress']}%)")
        st.progress(goal['progress'] / 100)
        st.caption(f"Target: {goal['target']}")

st.divider()

# Category breakdown
st.subheader("🥧 Expense Distribution")

col1, col2 = st.columns(2)

with col1:
    # Pie chart
    fig3 = go.Figure(data=[go.Pie(
        labels=categories,
        values=amounts,
        hole=0.3
    )])

    fig3.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("### Category Analysis")
    st.write("**Top Spending Categories:**")

    for cat, amt in sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)[:3]:
        percentage = (amt / sum(amounts)) * 100
        st.write(f"- **{cat}**: ₹{amt:,} ({percentage:.1f}%)")

    st.divider()

    st.write("**Budget Status:**")
    st.write("- 🟢 Within budget: 4 categories")
    st.write("- 🟡 Near limit: 1 category")
    st.write("- 🔴 Over budget: 1 category")
