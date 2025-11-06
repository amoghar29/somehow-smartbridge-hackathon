"""
Goals page - Set and track financial goals with AI recommendations.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api_client import APIClient
from config.settings import BACKEND_URL

st.set_page_config(page_title="Goals", page_icon="🎯", layout="wide")

# Initialize API client
api_client = APIClient(BACKEND_URL)

st.title("🎯 Financial Goals")

# Check backend connection
if not api_client.check_health():
    st.error("⚠️ Backend server is not running! Please start it at http://localhost:8000")
    st.info("Run: `cd backend && python main.py`")
    st.stop()

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login to view your goals")
    st.stop()

# Initialize goals in session state
if 'goals' not in st.session_state:
    st.session_state.goals = [
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

# Store AI recommendations in session state
if 'ai_recommendations' not in st.session_state:
    st.session_state.ai_recommendations = None

# Initialize form defaults - CRITICAL for preventing white page
def init_form_defaults():
    """Initialize all form session state values with defaults"""
    defaults = {
        'form_goal_name': "",
        'form_target_amount': 100000,
        'form_current_savings': 10000,
        'form_target_date': datetime.now().date(),
        'form_category': "Travel",
        'form_goal_type': "Short Term (<1 year)"
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Call initialization
init_form_defaults()

# Goal creation section
with st.expander("➕ Create New Goal", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        goal_name = st.text_input(
            "Goal Name",
            value=st.session_state.form_goal_name,
            placeholder="e.g., Dream Vacation",
            key="input_goal_name"
        )
        target_amount = st.number_input(
            "Target Amount (₹)",
            min_value=1000,
            value=st.session_state.form_target_amount,
            step=1000,
            key="input_target_amount"
        )
        current_savings = st.number_input(
            "Current Savings (₹)",
            min_value=0,
            value=st.session_state.form_current_savings,
            step=1000,
            key="input_current_savings"
        )

    with col2:
        goal_type_options = ["Short Term (<1 year)", "Medium Term (1-3 years)", "Long Term (>3 years)"]
        goal_type_index = goal_type_options.index(st.session_state.form_goal_type) if st.session_state.form_goal_type in goal_type_options else 0
        goal_type = st.selectbox(
            "Goal Type",
            goal_type_options,
            index=goal_type_index,
            key="input_goal_type"
        )

        target_date = st.date_input(
            "Target Date",
            value=st.session_state.form_target_date,
            min_value=datetime.now().date(),
            key="input_target_date"
        )

        category_options = ["Travel", "Education", "Emergency Fund", "Home", "Car", "Retirement", "Other"]
        category_index = category_options.index(st.session_state.form_category) if st.session_state.form_category in category_options else 0
        category = st.selectbox(
            "Category",
            category_options,
            index=category_index,
            key="input_category"
        )

    # AI-powered planning
    if st.button("🤖 Get AI Recommendations"):
        if not goal_name:
            st.error("Please enter a goal name")
        elif target_amount <= current_savings:
            st.error("Target amount must be greater than current savings")
        else:
            # Save form values to session state BEFORE making API call
            st.session_state.form_goal_name = goal_name
            st.session_state.form_target_amount = target_amount
            st.session_state.form_current_savings = current_savings
            st.session_state.form_goal_type = goal_type
            st.session_state.form_target_date = target_date
            st.session_state.form_category = category

            try:
                with st.spinner("🤖 AI is analyzing your financial situation..."):
                    # Calculate months until target date
                    months_until_target = max(1, (target_date - datetime.now().date()).days // 30)

                    # Get user income (default if not set)
                    user_income = st.session_state.get('monthly_income', 50000)

                    # Call the real AI API
                    result = api_client.create_goal_plan(
                        goal_name=goal_name,
                        target_amount=target_amount,
                        months=months_until_target,
                        income=user_income,
                        persona="professional"
                    )

                    if result and 'advice' in result:
                        st.session_state.ai_recommendations = result
                        st.rerun()
                    else:
                        st.error("Failed to get AI recommendations. Please try again.")
            except Exception as e:
                st.error(f"Error getting AI recommendations: {str(e)}")
                st.info("Please make sure the backend server is running.")

# Display AI recommendations if available (OUTSIDE the expander)
if st.session_state.ai_recommendations:
    st.divider()

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🤖 AI-Powered Recommendations")
    with col2:
        if st.button("🔄 Start Over", key="clear_recommendations"):
            st.session_state.ai_recommendations = None
            st.rerun()

    # Show goal summary
    st.info(f"**Goal:** {st.session_state.form_goal_name} | **Target:** ₹{st.session_state.form_target_amount:,.0f} | **Current Savings:** ₹{st.session_state.form_current_savings:,.0f}")

    try:
        result = st.session_state.ai_recommendations

        # Display AI advice
        with st.container():
            st.markdown("#### 💡 AI Analysis")
            st.write(result.get('advice', 'No advice available'))

        # Calculate different plan scenarios using session state values
        remaining = st.session_state.form_target_amount - st.session_state.form_current_savings
        months_until_target = max(1, (st.session_state.form_target_date - datetime.now().date()).days // 30)

        # Easy plan: extend timeline by 50%
        easy_months = int(months_until_target * 1.5)
        easy_monthly = remaining / easy_months if easy_months > 0 else 0

        # Moderate plan: original timeline
        moderate_monthly = remaining / months_until_target if months_until_target > 0 else 0

        # Aggressive plan: reduce timeline by 40%
        aggressive_months = max(1, int(months_until_target * 0.6))
        aggressive_monthly = remaining / aggressive_months if aggressive_months > 0 else 0

        tab1, tab2, tab3 = st.tabs(["💚 Easy Plan", "💛 Moderate Plan", "❤️ Aggressive Plan"])

        with tab1:
            st.markdown(f"""
            **Easy Savings Plan** (Minimal lifestyle impact)
            - **Monthly Savings Required**: ₹{easy_monthly:,.0f}
            - **Time to Goal**: {easy_months} months
            - **Feasibility**: High ✅

            **How to achieve:**
            - Automate savings on payday
            - Reduce discretionary spending by small amounts
            - Flexible timeline gives you breathing room
            """)

            if st.button("Choose Easy Plan", key="easy_plan"):
                new_goal = {
                    "name": st.session_state.form_goal_name,
                    "target": st.session_state.form_target_amount,
                    "current": st.session_state.form_current_savings,
                    "category": st.session_state.form_category,
                    "deadline": (datetime.now() + timedelta(days=easy_months*30)).strftime("%b %Y"),
                    "monthly_required": int(easy_monthly)
                }
                st.session_state.goals.append(new_goal)
                st.session_state.ai_recommendations = None
                st.success(f"✅ Goal '{st.session_state.form_goal_name}' created with Easy plan!")
                st.rerun()

        with tab2:
            st.markdown(f"""
            **Moderate Savings Plan** (Some lifestyle adjustments)
            - **Monthly Savings Required**: ₹{moderate_monthly:,.0f}
            - **Time to Goal**: {months_until_target} months
            - **Feasibility**: Medium ⚠️

            **How to achieve:**
            - Cut one major expense category
            - Increase savings rate gradually
            - Stay focused on your goal deadline
            """)

            if st.button("Choose Moderate Plan", key="moderate_plan"):
                new_goal = {
                    "name": st.session_state.form_goal_name,
                    "target": st.session_state.form_target_amount,
                    "current": st.session_state.form_current_savings,
                    "category": st.session_state.form_category,
                    "deadline": st.session_state.form_target_date.strftime("%b %Y"),
                    "monthly_required": int(moderate_monthly)
                }
                st.session_state.goals.append(new_goal)
                st.session_state.ai_recommendations = None
                st.success(f"✅ Goal '{st.session_state.form_goal_name}' created with Moderate plan!")
                st.rerun()

        with tab3:
            st.markdown(f"""
            **Aggressive Savings Plan** (Significant changes needed)
            - **Monthly Savings Required**: ₹{aggressive_monthly:,.0f}
            - **Time to Goal**: {aggressive_months} months
            - **Feasibility**: Challenging ❌

            **How to achieve:**
            - Cut all non-essential expenses
            - Maximize available savings
            - Consider additional income sources
            """)

            if st.button("Choose Aggressive Plan", key="aggressive_plan"):
                new_goal = {
                    "name": st.session_state.form_goal_name,
                    "target": st.session_state.form_target_amount,
                    "current": st.session_state.form_current_savings,
                    "category": st.session_state.form_category,
                    "deadline": (datetime.now() + timedelta(days=aggressive_months*30)).strftime("%b %Y"),
                    "monthly_required": int(aggressive_monthly)
                }
                st.session_state.goals.append(new_goal)
                st.session_state.ai_recommendations = None
                st.success(f"✅ Goal '{st.session_state.form_goal_name}' created with Aggressive plan!")
                st.rerun()

    except Exception as e:
        st.error(f"Error displaying recommendations: {str(e)}")
        st.session_state.ai_recommendations = None
        st.rerun()

st.divider()

# Display active goals
st.subheader("📋 Your Active Goals")

# Get goals from session state
goals = st.session_state.goals

if not goals:
    st.info("No goals yet. Create your first goal above!")
else:
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
