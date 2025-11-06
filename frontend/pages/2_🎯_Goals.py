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

# Initialize financial data in session state if not present
if 'monthly_income' not in st.session_state:
    st.session_state.monthly_income = 1358419.20
if 'total_expenses' not in st.session_state:
    st.session_state.total_expenses = 35000

# Initialize goals in session state
if 'goals' not in st.session_state:
    st.session_state.goals = [
        {
            "name": "Emergency Fund",
            "target": 300000,
            "current": 180000,
            "category": "Emergency Fund",
            "deadline": "Dec 2025",
            "monthly_required": 10000,
            "description": "Build a safety net to cover 6 months of expenses for unexpected situations"
        },
        {
            "name": "Dream Vacation to Europe",
            "target": 150000,
            "current": 52500,
            "category": "Travel",
            "deadline": "Jun 2025",
            "monthly_required": 12000,
            "description": "Two-week trip to visit Paris, Rome, and Barcelona"
        },
        {
            "name": "New Laptop",
            "target": 80000,
            "current": 64000,
            "category": "Other",
            "deadline": "Jan 2025",
            "monthly_required": 8000,
            "description": "High-performance laptop for work and personal projects"
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
        'form_goal_type': "Short Term (<1 year)",
        'form_description': ""
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
        description = st.text_area(
            "Description",
            value=st.session_state.form_description,
            placeholder="Describe your goal...",
            key="input_description",
            height=100
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
            st.session_state.form_description = description

            try:
                with st.spinner("🤖 AI is analyzing your financial situation..."):
                    # Calculate months until target date
                    months_until_target = max(1, (target_date - datetime.now().date()).days // 30)

                    # Get user income and expenses (use defaults if not set)
                    user_income = st.session_state.get('monthly_income', 1358419.20)
                    user_expenses = st.session_state.get('total_expenses', 35000)

                    # Ensure income is not 0
                    if user_income == 0:
                        user_income = 1358419.20

                    # Call the real AI API with income and expenses
                    result = api_client.create_goal_plan(
                        goal_name=goal_name,
                        target_amount=target_amount,
                        months=months_until_target,
                        income=user_income,
                        expenses=user_expenses,
                        current_savings=current_savings,
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
                    "monthly_required": int(easy_monthly),
                    "description": st.session_state.form_description
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
                    "monthly_required": int(moderate_monthly),
                    "description": st.session_state.form_description
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
                    "monthly_required": int(aggressive_monthly),
                    "description": st.session_state.form_description
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
                if goal.get('description'):
                    st.markdown(f"*{goal['description']}*")

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

            # Initialize session state for contribution and edit modes
            if f'show_contribution_{goal["name"]}' not in st.session_state:
                st.session_state[f'show_contribution_{goal["name"]}'] = False
            if f'show_edit_{goal["name"]}' not in st.session_state:
                st.session_state[f'show_edit_{goal["name"]}'] = False

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("💰 Add Contribution", key=f"add_{goal['name']}"):
                    st.session_state[f'show_contribution_{goal["name"]}'] = not st.session_state[f'show_contribution_{goal["name"]}']
                    st.session_state[f'show_edit_{goal["name"]}'] = False
                    st.rerun()
            with col_b:
                if st.button("✏️ Edit Goal", key=f"edit_{goal['name']}"):
                    st.session_state[f'show_edit_{goal["name"]}'] = not st.session_state[f'show_edit_{goal["name"]}']
                    st.session_state[f'show_contribution_{goal["name"]}'] = False
                    st.rerun()
            with col_c:
                if st.button("📊 View Details", key=f"view_{goal['name']}"):
                    with st.expander("Goal Details", expanded=True):
                        st.markdown(f"""
                        **Goal Name:** {goal['name']}

                        **Description:** {goal.get('description', 'No description provided')}

                        **Category:** {goal['category']}

                        **Target Amount:** ₹{goal['target']:,}

                        **Current Savings:** ₹{goal['current']:,}

                        **Remaining:** ₹{goal['target'] - goal['current']:,}

                        **Monthly Required:** ₹{goal['monthly_required']:,}

                        **Deadline:** {goal['deadline']}

                        **Progress:** {progress:.1f}%
                        """)

            # Add Contribution Form
            if st.session_state[f'show_contribution_{goal["name"]}']:
                with st.container():
                    st.markdown("#### 💰 Add Contribution")
                    contribution_col1, contribution_col2 = st.columns([2, 1])

                    with contribution_col1:
                        contribution_amount = st.number_input(
                            "Contribution Amount (₹)",
                            min_value=1,
                            max_value=goal['target'] - goal['current'],
                            value=min(5000, goal['target'] - goal['current']),
                            step=100,
                            key=f"contribution_amount_{goal['name']}"
                        )
                        contribution_note = st.text_input(
                            "Note (optional)",
                            placeholder="e.g., Monthly savings",
                            key=f"contribution_note_{goal['name']}"
                        )

                    with contribution_col2:
                        new_total = goal['current'] + contribution_amount
                        new_progress = (new_total / goal['target']) * 100
                        st.metric("New Total", f"₹{new_total:,}")
                        st.metric("New Progress", f"{new_progress:.1f}%")

                    submit_col1, submit_col2 = st.columns([1, 1])
                    with submit_col1:
                        if st.button("✅ Submit Contribution", key=f"submit_contribution_{goal['name']}"):
                            # Find and update the goal
                            for g in st.session_state.goals:
                                if g['name'] == goal['name']:
                                    g['current'] += contribution_amount
                                    break
                            st.session_state[f'show_contribution_{goal["name"]}'] = False
                            st.success(f"✅ Added ₹{contribution_amount:,} to {goal['name']}!")
                            st.rerun()

                    with submit_col2:
                        if st.button("❌ Cancel", key=f"cancel_contribution_{goal['name']}"):
                            st.session_state[f'show_contribution_{goal["name"]}'] = False
                            st.rerun()

            # Edit Goal Form
            if st.session_state[f'show_edit_{goal["name"]}']:
                with st.container():
                    st.markdown("#### ✏️ Edit Goal")
                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:
                        edit_name = st.text_input(
                            "Goal Name",
                            value=goal['name'],
                            key=f"edit_name_{goal['name']}"
                        )
                        edit_description = st.text_area(
                            "Description",
                            value=goal.get('description', ''),
                            key=f"edit_description_{goal['name']}",
                            height=100
                        )
                        edit_target = st.number_input(
                            "Target Amount (₹)",
                            min_value=goal['current'] + 1000,
                            value=goal['target'],
                            step=1000,
                            key=f"edit_target_{goal['name']}"
                        )

                    with edit_col2:
                        edit_category = st.selectbox(
                            "Category",
                            ["Travel", "Education", "Emergency Fund", "Home", "Car", "Retirement", "Other"],
                            index=["Travel", "Education", "Emergency Fund", "Home", "Car", "Retirement", "Other"].index(goal['category']) if goal['category'] in ["Travel", "Education", "Emergency Fund", "Home", "Car", "Retirement", "Other"] else 0,
                            key=f"edit_category_{goal['name']}"
                        )
                        edit_monthly = st.number_input(
                            "Monthly Required (₹)",
                            min_value=0,
                            value=goal['monthly_required'],
                            step=500,
                            key=f"edit_monthly_{goal['name']}"
                        )
                        edit_deadline = st.text_input(
                            "Deadline",
                            value=goal['deadline'],
                            key=f"edit_deadline_{goal['name']}"
                        )

                    submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 1])
                    with submit_col1:
                        if st.button("✅ Save Changes", key=f"submit_edit_{goal['name']}"):
                            # Find and update the goal
                            for g in st.session_state.goals:
                                if g['name'] == goal['name']:
                                    g['name'] = edit_name
                                    g['description'] = edit_description
                                    g['target'] = edit_target
                                    g['category'] = edit_category
                                    g['monthly_required'] = edit_monthly
                                    g['deadline'] = edit_deadline
                                    break
                            st.session_state[f'show_edit_{goal["name"]}'] = False
                            st.success(f"✅ Updated {edit_name}!")
                            st.rerun()

                    with submit_col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_{goal['name']}"):
                            st.session_state[f'show_edit_{goal["name"]}'] = False
                            st.rerun()

                    with submit_col3:
                        if st.button("🗑️ Delete Goal", key=f"delete_{goal['name']}"):
                            st.session_state.goals = [g for g in st.session_state.goals if g['name'] != goal['name']]
                            st.session_state[f'show_edit_{goal["name"]}'] = False
                            st.warning(f"🗑️ Deleted {goal['name']}")
                            st.rerun()

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
