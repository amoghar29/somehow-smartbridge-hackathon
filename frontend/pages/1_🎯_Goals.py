"""
Goals Planning Page - AI-powered goal planning
"""

import streamlit as st
from utils.api_client import APIClient
from config.settings import BACKEND_URL
import plotly.graph_objects as go

st.set_page_config(page_title="Goals Planning", page_icon="🎯", layout="wide")

# Initialize API client
api_client = APIClient(BACKEND_URL)

st.title("🎯 Financial Goals Planning")

# Check backend connection
if not api_client.check_health():
    st.error("⚠️ Backend server is not running! Please start it at http://localhost:8000")
    st.stop()

st.write("Create and track your financial goals with AI-powered recommendations.")

# Goal creation section
st.subheader("➕ Create New Goal")

with st.form("goal_form"):
    col1, col2 = st.columns(2)

    with col1:
        goal_name = st.text_input("Goal Name", placeholder="e.g., Emergency Fund")
        target_amount = st.number_input("Target Amount (₹)", min_value=1000, value=100000, step=5000)
        current_savings = st.number_input("Current Savings (₹)", min_value=0, value=0, step=1000)

    with col2:
        monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=60000, step=5000)
        months = st.slider("Timeline (months)", min_value=1, max_value=60, value=12)
        persona = st.selectbox("Risk Profile", ["conservative", "professional", "aggressive"])

    submit_goal = st.form_submit_button("🤖 Get AI-Powered Plan", use_container_width=True)

if submit_goal and goal_name:
    st.divider()
    st.subheader("🤖 AI-Generated Savings Plan")

    with st.spinner("AI is creating your personalized savings plan..."):
        # Call backend AI goal planner
        result = api_client.create_goal_plan(
            goal_name=goal_name,
            target_amount=target_amount,
            months=months,
            income=monthly_income,
            persona=persona
        )

    if result:
        # Display plan
        if "plan" in result:
            st.success("✅ Goal plan created successfully!")
            st.markdown(f"**Plan Details:**\n\n{result['plan']}")

        # Display AI advice
        if "advice" in result:
            st.info(f"**💡 AI Advice:**\n\n{result['advice']}")

        # Calculate and display progress metrics
        monthly_required = (target_amount - current_savings) / months if months > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Target Amount", f"₹{target_amount:,.0f}")
        with col2:
            st.metric("Monthly Savings Needed", f"₹{monthly_required:,.0f}")
        with col3:
            percentage_of_income = (monthly_required / monthly_income * 100) if monthly_income > 0 else 0
            st.metric("% of Income", f"{percentage_of_income:.1f}%")

        # Progress visualization
        st.subheader("📊 Goal Progress Visualization")

        progress_percentage = (current_savings / target_amount * 100) if target_amount > 0 else 0

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=progress_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Progress toward {goal_name}"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "#e0e7ff"},
                    {'range': [50, 75], 'color': "#c7d2fe"},
                    {'range': [75, 100], 'color': "#a5b4fc"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Savings projection
        st.subheader("📈 Savings Projection")

        months_list = list(range(months + 1))
        projected_savings = [current_savings + (monthly_required * m) for m in months_list]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months_list,
            y=projected_savings,
            mode='lines+markers',
            name='Projected Savings',
            fill='tozeroy',
            line=dict(color='#667eea', width=3)
        ))

        fig2.add_hline(
            y=target_amount,
            line_dash="dash",
            line_color="green",
            annotation_text="Target Amount"
        )

        fig2.update_layout(
            xaxis_title="Months",
            yaxis_title="Savings (₹)",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.02)',
            hovermode='x unified'
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("Failed to generate goal plan. Please try again.")

# Tips section
st.divider()
st.subheader("💡 Goal Planning Tips")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 SMART Goals**
    - Specific and clear
    - Measurable targets
    - Achievable timeline
    - Realistic amounts
    - Time-bound plan
    """)

with col2:
    st.markdown("""
    **💰 Savings Strategies**
    - Automate savings
    - 50-30-20 rule
    - Cut unnecessary expenses
    - Increase income streams
    - Track progress regularly
    """)

with col3:
    st.markdown("""
    **📊 Investment Options**
    - Fixed Deposits (Safe)
    - Mutual Funds (Moderate)
    - PPF/EPF (Tax saving)
    - Emergency liquid funds
    - Diversify portfolio
    """)
