"""
Goals page - Set and track financial goals with AI recommendations.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Goals", page_icon="🎯", layout="wide")

st.title("🎯 Financial Goals")

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login to view your goals")
    st.stop()

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

st.divider()

# Display active goals
st.subheader("📋 Your Active Goals")

# Sample goals data
goals = [
    {
        "name": "Emergency Fund",
        "target": 300000,
        "current": 180000,
        "category": "Emergency Fund",
        "deadline": "Dec 2025",
        "monthly_required": 10000
    },
    {
        "name": "Dream Vacation to Europe",
        "target": 150000,
        "current": 52500,
        "category": "Travel",
        "deadline": "Jun 2025",
        "monthly_required": 12000
    },
    {
        "name": "New Laptop",
        "target": 80000,
        "current": 64000,
        "category": "Other",
        "deadline": "Jan 2025",
        "monthly_required": 8000
    }
]

for goal in goals:
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"### {goal['name']}")
            st.caption(f"Category: {goal['category']} | Deadline: {goal['deadline']}")

            # Progress bar
            progress = (goal['current'] / goal['target']) * 100
            st.progress(progress / 100)
            st.write(f"Progress: {progress:.1f}% (₹{goal['current']:,} / ₹{goal['target']:,})")

        with col2:
            st.metric("Monthly Target", f"₹{goal['monthly_required']:,}")
            remaining = goal['target'] - goal['current']
            st.metric("Remaining", f"₹{remaining:,}")

        with col3:
            # Gauge chart for progress
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progress,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "lightblue"},
                        {'range': [75, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))

            fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("💰 Add Contribution", key=f"add_{goal['name']}"):
                st.info("Contribution form will appear here")
        with col_b:
            if st.button("✏️ Edit Goal", key=f"edit_{goal['name']}"):
                st.info("Edit form will appear here")
        with col_c:
            if st.button("📊 View Details", key=f"view_{goal['name']}"):
                st.info("Detailed view will appear here")

        st.divider()

# Goals insights
st.subheader("💡 Goal Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 On Track Goals**
    - Emergency Fund (60%)
    - New Laptop (80%)

    You're making great progress!
    """)

with col2:
    st.markdown("""
    **⚠️ Needs Attention**
    - Dream Vacation (35%)

    Consider increasing monthly contributions by ₹3,000 to stay on track.
    """)

with col3:
    st.markdown("""
    **📈 Recommendations**
    - Increase savings rate by 5%
    - Cut discretionary spending by ₹2,000/month
    - Consider side income opportunities
    """)
