"""
Dashboard page - Overview of financial status and recent activity.
Now with full backend integration and interactive modals!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config.settings import BACKEND_URL
from utils.api_client import APIClient
from components.modals import transaction_modal, show_notification

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient(BACKEND_URL)

api_client = st.session_state.api_client

# Custom CSS for better UI
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .add-transaction-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 30px;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 999;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .transaction-item {
        background: rgba(255,255,255,0.05);
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Header with action button
col_header, col_btn = st.columns([3, 1])
with col_header:
    st.title("📊 Financial Dashboard")
with col_btn:
    if st.button("➕ Add Transaction", use_container_width=True, type="primary"):
        st.session_state.show_transaction_modal = True

# Show transaction modal
if st.session_state.get("show_transaction_modal", False):
    with st.container():
        transaction_modal(api_client, on_success=lambda: st.session_state.update(show_transaction_modal=False))

        # Add close button
        if st.button("✖ Cancel", key="close_modal"):
            st.session_state.show_transaction_modal = False
            st.rerun()
    st.divider()

# Check authentication (demo mode - always authenticated)
if not st.session_state.get('authenticated', False):
    st.session_state.authenticated = True

# Backend health check
with st.spinner("Connecting to backend..."):
    backend_status = api_client.check_health()

if not backend_status:
    st.error("⚠️ Backend is not running. Please start the backend server at http://localhost:8000")
    st.info("💡 Run `python backend/main.py` to start the backend")
    st.stop()

# Fetch real analytics data
with st.spinner("Loading your financial data..."):
    analytics_data = api_client.get_analytics()
    transactions = api_client.get_transactions(limit=20)

# Extract analytics
totals = analytics_data.get("totals", {})
income = totals.get("income", 0)
expenses = totals.get("expenses", 0)
savings = totals.get("savings", 0)
savings_rate = totals.get("savings_rate", 0)

# Calculate deltas (mock for demo - can be calculated from historical data)
income_delta = "+5%"
expenses_delta = "-3%"
savings_delta = "+12%"
rate_delta = "+2%"

# Key metrics with real data
st.markdown("### 💰 Financial Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Income", f"₹{income:,.2f}", income_delta)
with col2:
    st.metric("Total Expenses", f"₹{expenses:,.2f}", expenses_delta)
with col3:
    st.metric("Net Savings", f"₹{savings:,.2f}", savings_delta)
with col4:
    st.metric("Savings Rate", f"{savings_rate:.1f}%", rate_delta)

st.divider()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Spending trends from backend
    st.subheader("📈 Spending by Category")

    if transactions:
        # Calculate category totals from transactions
        df_transactions = pd.DataFrame(transactions)

        # Filter expenses only
        expense_txns = df_transactions[df_transactions['type'] == 'expense']

        if not expense_txns.empty:
            category_totals = expense_txns.groupby('category')['amount'].sum().reset_index()
            category_totals = category_totals.sort_values('amount', ascending=False)

            fig = go.Figure(data=[
                go.Bar(
                    x=category_totals['category'],
                    y=category_totals['amount'],
                    marker_color='#667eea',
                    text=category_totals['amount'].apply(lambda x: f'₹{x:,.0f}'),
                    textposition='auto'
                )
            ])

            fig.update_layout(
                height=300,
                xaxis_title="Category",
                yaxis_title="Amount (₹)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.02)',
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense transactions found. Add some expenses to see the chart!")
    else:
        st.info("No transaction data available. Add your first transaction!")

    # Spending over time from backend trend data
    st.subheader("📉 Transaction Timeline")

    trend_data = analytics_data.get("trend_data", [])

    if trend_data and len(trend_data) > 0:
        df_trend = pd.DataFrame(trend_data)

        # Backend returns 'month' field, not 'date'
        if 'month' in df_trend.columns:
            # Use month as x-axis
            fig2 = go.Figure()

            # Add income line
            fig2.add_trace(go.Scatter(
                x=df_trend['month'],
                y=df_trend['income'],
                mode='lines+markers',
                name='Income',
                line=dict(color='#84fab0', width=3),
                marker=dict(size=8)
            ))

            # Add expense line
            fig2.add_trace(go.Scatter(
                x=df_trend['month'],
                y=df_trend['expenses'],
                mode='lines+markers',
                name='Expenses',
                line=dict(color='#f5576c', width=3),
                marker=dict(size=8)
            ))

            fig2.update_layout(
                height=300,
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.02)',
                hovermode='x unified'
            )

            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Trend data format not recognized")
    else:
        st.info("Add more transactions to see spending trends over time")

with col2:
    st.subheader("📋 Recent Transactions")

    if transactions:
        # Display transactions
        for txn in transactions[:10]:  # Show last 10
            txn_type = txn.get('type', 'expense')
            amount = txn.get('amount', 0)
            description = txn.get('description', 'No description')
            category = txn.get('category', 'Other')
            date_str = txn.get('date', '')

            # Parse date
            try:
                txn_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_display = txn_date.strftime("%b %d")
            except:
                date_display = "Unknown"

            # Color based on type
            color = "green" if txn_type == "income" else "red"
            sign = "+" if txn_type == "income" else "-"
            icon = "💰" if txn_type == "income" else "💸"

            with st.container():
                st.markdown(f"""
                <div class="transaction-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{icon} {description}</strong><br>
                            <small style="color: #888;">{date_display} • {category}</small>
                        </div>
                        <div style="color: {color}; font-weight: bold; font-size: 16px;">
                            {sign}₹{amount:,.2f}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No transactions yet. Click 'Add Transaction' to get started!")

    st.divider()

    # Active goals
    st.subheader("🎯 Active Goals")

    if st.session_state.get("active_goals"):
        for goal in st.session_state.active_goals[:3]:  # Show top 3
            name = goal.get("name", "Unnamed Goal")
            current = goal.get("current", 0)
            target = goal.get("target", 1)
            progress = min((current / target) * 100, 100)

            st.write(f"**{name}** ({progress:.0f}%)")
            st.progress(progress / 100)
            st.caption(f"₹{current:,.2f} / ₹{target:,.2f}")
            st.markdown("")
    else:
        st.info("No active goals. Visit the Goals page to create one!")

st.divider()

# Category breakdown with real data
st.subheader("🥧 Expense Analysis")

col1, col2 = st.columns(2)

with col1:
    if transactions:
        df_transactions = pd.DataFrame(transactions)
        expense_txns = df_transactions[df_transactions['type'] == 'expense']

        if not expense_txns.empty:
            category_totals = expense_txns.groupby('category')['amount'].sum().reset_index()

            # Pie chart
            fig3 = go.Figure(data=[go.Pie(
                labels=category_totals['category'],
                values=category_totals['amount'],
                hole=0.4,
                marker=dict(colors=px.colors.sequential.Purples_r)
            )])

            fig3.update_layout(
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True
            )

            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Add expense transactions to see the breakdown")
    else:
        st.info("No data available for expense distribution")

with col2:
    st.markdown("### 📊 Category Insights")

    if transactions:
        df_transactions = pd.DataFrame(transactions)
        expense_txns = df_transactions[df_transactions['type'] == 'expense']

        if not expense_txns.empty:
            category_totals = expense_txns.groupby('category')['amount'].sum().reset_index()
            category_totals = category_totals.sort_values('amount', ascending=False)
            total_expenses = category_totals['amount'].sum()

            st.write("**Top Spending Categories:**")
            for idx, row in category_totals.head(5).iterrows():
                category = row['category']
                amount = row['amount']
                percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
                st.write(f"- **{category}**: ₹{amount:,.2f} ({percentage:.1f}%)")
        else:
            st.info("Add expenses to see category insights")
    else:
        st.info("No transaction data available")

# Footer info
st.divider()
st.caption("💡 Tip: Click 'Add Transaction' to record your income and expenses in real-time!")
