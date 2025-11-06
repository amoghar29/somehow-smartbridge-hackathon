"""
Modal/Dialog components for Streamlit.
Provides forms for better UX.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Callable
from config.settings import TRANSACTION_CATEGORIES, GOAL_CATEGORIES


def transaction_modal(api_client, on_success: Optional[Callable] = None):
    """
    Modal dialog for adding a new transaction.

    Args:
        api_client: APIClient instance
        on_success: Callback function to execute after successful transaction creation
    """
    st.markdown("## 💰 Add Transaction")
    st.divider()

    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            transaction_type = st.selectbox(
                "Type",
                ["income", "expense"],
                format_func=lambda x: "💰 Income" if x == "income" else "💸 Expense"
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

        with col2:
            category = st.selectbox(
                "Category",
                ["Salary", "Freelance", "Investment Returns", "Other"] if transaction_type == "income"
                else TRANSACTION_CATEGORIES
            )

            date = st.date_input(
                "Date",
                value=datetime.now()
            )

        description = st.text_input(
            "Description",
            placeholder="e.g., Monthly salary, Grocery shopping, etc."
        )

        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Add Transaction", use_container_width=True, type="primary")

        if submitted:
            if amount <= 0:
                st.error("Please enter a valid amount greater than 0")
                return

            if not description:
                st.error("Please enter a description")
                return

            # Prepare transaction data
            transaction_data = {
                "description": description,
                "amount": float(amount),
                "category": category,
                "type": transaction_type,
                "date": date.isoformat()
            }

            # Show loading
            with st.spinner("Adding transaction..."):
                result = api_client.create_transaction(transaction_data)

            if result.get("success"):
                st.success(f"✅ Transaction added successfully!")

                # Call success callback if provided
                if on_success:
                    on_success()

                # Close modal after 1 second
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ Failed to add transaction: {result.get('message', 'Unknown error')}")


def goal_create_modal(api_client, on_success: Optional[Callable] = None):
    """
    Modal dialog for creating a new financial goal with AI planning.

    Args:
        api_client: APIClient instance
        on_success: Callback function to execute after successful goal creation
    """
    st.markdown("### Set Your Financial Goal")

    with st.form("goal_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            goal_name = st.text_input(
                "Goal Name",
                placeholder="e.g., Emergency Fund, Vacation to Bali"
            )

            target_amount = st.number_input(
                "Target Amount (₹)",
                min_value=1000.0,
                step=1000.0,
                format="%.2f"
            )

            category = st.selectbox(
                "Category",
                GOAL_CATEGORIES
            )

        with col2:
            current_savings = st.number_input(
                "Current Savings (₹)",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                help="Amount already saved towards this goal"
            )

            months = st.number_input(
                "Time Period (Months)",
                min_value=1,
                max_value=360,
                value=12,
                step=1
            )

            monthly_income = st.number_input(
                "Monthly Income (₹)",
                min_value=0.0,
                step=5000.0,
                format="%.2f",
                help="Your monthly income for planning"
            )

        persona = st.selectbox(
            "Financial Profile",
            ["student", "professional", "general"],
            format_func=lambda x: x.title(),
            help="Helps AI provide personalized advice"
        )

        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Create Goal Plan", use_container_width=True, type="primary")

        if submitted:
            # Validation
            if not goal_name:
                st.error("Please enter a goal name")
                return

            if target_amount <= 0:
                st.error("Please enter a valid target amount")
                return

            if monthly_income <= 0:
                st.error("Please enter your monthly income")
                return

            # Calculate required monthly savings
            monthly_target = (target_amount - current_savings) / months if months > 0 else 0
            percentage_of_income = (monthly_target / monthly_income * 100) if monthly_income > 0 else 0

            # Create goal plan using AI
            with st.spinner("🤖 Creating personalized savings plan with AI..."):
                # Create comprehensive goal planning question
                question = f"""Help me plan for this financial goal:

Goal: {goal_name}
Category: {category}
Target Amount: ₹{target_amount:,.0f}
Current Savings: ₹{current_savings:,.0f}
Remaining to Save: ₹{target_amount - current_savings:,.0f}
Timeline: {months} months
Monthly Income: ₹{monthly_income:,.0f}
Required Monthly Savings: ₹{monthly_target:,.0f} ({percentage_of_income:.1f}% of income)

Please provide:
1. A brief analysis of the goal feasibility
2. Step-by-step action plan to achieve this goal
3. Recommended investment strategies based on the timeline
4. Tips for staying on track and maintaining discipline
5. Potential challenges and how to overcome them"""

                # Call AI using get_ai_advice
                ai_advice = api_client.get_ai_advice(question, persona=persona)

            if ai_advice and not ai_advice.startswith("Error"):
                st.success("✅ Goal plan created successfully!")

                # Display the plan
                st.markdown("### 📊 Your Savings Plan")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Monthly Savings", f"₹{monthly_target:,.2f}")
                with col2:
                    st.metric("% of Income", f"{percentage_of_income:.1f}%")
                with col3:
                    feasibility = "Easy" if percentage_of_income < 20 else "Moderate" if percentage_of_income < 40 else "Challenging"
                    st.metric("Feasibility", feasibility)

                # AI Advice
                st.info(f"💡 **AI Advice:**\n\n{ai_advice}")

                # Save to session state
                if "active_goals" not in st.session_state:
                    st.session_state.active_goals = []

                st.session_state.active_goals.append({
                    "id": f"goal_{len(st.session_state.active_goals) + 1}",
                    "name": goal_name,
                    "target": target_amount,
                    "current": current_savings,
                    "months": months,
                    "category": category,
                    "monthly_savings": monthly_target,
                    "percentage": percentage_of_income,
                    "feasibility": feasibility,
                    "advice": ai_advice,
                    "created_at": datetime.now().isoformat()
                })

                if on_success:
                    on_success()

                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to create goal plan. Please try again.")


def goal_edit_modal(goal_data: Dict, api_client, on_success: Optional[Callable] = None):
    """
    Modal dialog for editing an existing goal.

    Args:
        goal_data: Existing goal data dictionary
        api_client: APIClient instance
        on_success: Callback function to execute after successful update
    """
    st.markdown(f"### Edit Goal: {goal_data.get('name', 'Unknown')}")

    with st.form("goal_edit_form"):
        col1, col2 = st.columns(2)

        with col1:
            goal_name = st.text_input(
                "Goal Name",
                value=goal_data.get("name", "")
            )

            target_amount = st.number_input(
                "Target Amount (₹)",
                value=float(goal_data.get("target", 0)),
                min_value=1000.0,
                step=1000.0,
                format="%.2f"
            )

            category = st.selectbox(
                "Category",
                GOAL_CATEGORIES,
                index=GOAL_CATEGORIES.index(goal_data.get("category", GOAL_CATEGORIES[0]))
                      if goal_data.get("category") in GOAL_CATEGORIES else 0
            )

        with col2:
            current_savings = st.number_input(
                "Current Progress (₹)",
                value=float(goal_data.get("current", 0)),
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            months = st.number_input(
                "Remaining Months",
                value=int(goal_data.get("months", 12)),
                min_value=1,
                max_value=360,
                step=1
            )

            status = st.selectbox(
                "Status",
                ["active", "completed", "paused"],
                format_func=lambda x: x.title()
            )

        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Update Goal", use_container_width=True, type="primary")

        if submitted:
            # Update goal in session state
            if "active_goals" in st.session_state:
                for i, goal in enumerate(st.session_state.active_goals):
                    if goal.get("id") == goal_data.get("id"):
                        st.session_state.active_goals[i].update({
                            "name": goal_name,
                            "target": target_amount,
                            "current": current_savings,
                            "months": months,
                            "category": category,
                            "status": status,
                            "updated_at": datetime.now().isoformat()
                        })
                        break

            st.success("✅ Goal updated successfully!")

            if on_success:
                on_success()

            st.rerun()


def add_contribution_modal(goal_data: Dict, on_success: Optional[Callable] = None):
    """
    Modal dialog for adding a contribution to a goal.

    Args:
        goal_data: Goal data dictionary
        on_success: Callback function after successful contribution
    """
    st.markdown(f"### Add Contribution to: {goal_data.get('name', 'Unknown')}")

    # Show current progress
    current = goal_data.get("current", 0)
    target = goal_data.get("target", 0)
    remaining = target - current

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current", f"₹{current:,.2f}")
    with col2:
        st.metric("Target", f"₹{target:,.2f}")
    with col3:
        st.metric("Remaining", f"₹{remaining:,.2f}")

    st.progress(min(current / target, 1.0))

    with st.form("contribution_form"):
        amount = st.number_input(
            "Contribution Amount (₹)",
            min_value=100.0,
            max_value=remaining,
            step=100.0,
            format="%.2f"
        )

        note = st.text_input(
            "Note (Optional)",
            placeholder="e.g., Monthly savings, Bonus"
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Add Contribution", use_container_width=True, type="primary")

        if submitted:
            if amount <= 0:
                st.error("Please enter a valid amount")
                return

            # Update goal in session state
            if "active_goals" in st.session_state:
                for i, goal in enumerate(st.session_state.active_goals):
                    if goal.get("id") == goal_data.get("id"):
                        st.session_state.active_goals[i]["current"] += amount

                        # Track contributions
                        if "contributions" not in st.session_state.active_goals[i]:
                            st.session_state.active_goals[i]["contributions"] = []

                        st.session_state.active_goals[i]["contributions"].append({
                            "amount": amount,
                            "note": note,
                            "date": datetime.now().isoformat()
                        })
                        break

            new_total = current + amount
            st.success(f"✅ Added ₹{amount:,.2f} to your goal!")
            st.info(f"New progress: ₹{new_total:,.2f} / ₹{target:,.2f} ({(new_total/target)*100:.1f}%)")

            if new_total >= target:
                st.balloons()
                st.success("🎉 Congratulations! You've reached your goal!")

            if on_success:
                on_success()

            st.rerun()


def show_notification(message: str, type: str = "success"):
    """
    Display a notification message.

    Args:
        message: Message to display
        type: Type of notification (success, error, warning, info)
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)
