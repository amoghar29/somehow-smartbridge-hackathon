"""
Goal Planning Agent
Creates savings plans and provides advice for financial goals
"""
from typing import Dict, Any
from core.granite_api import generate
from core.utils import calculate_monthly_savings_needed, format_currency
from core.logger import logger


def plan_goal(
    goal_name: str,
    target_amount: float,
    months: int,
    income: float,
    persona: str = "general",
    current_savings: float = 0.0
) -> Dict[str, Any]:
    """
    Create a savings plan for a financial goal

    Args:
        goal_name: Name of the financial goal
        target_amount: Target amount to save
        months: Number of months to reach the goal
        income: Monthly income
        persona: User persona
        current_savings: Current savings amount

    Returns:
        Dict containing plan details and AI advice
    """
    try:
        logger.info(f"Creating goal plan: {goal_name}")

        # Calculate required monthly savings
        monthly_needed = calculate_monthly_savings_needed(target_amount, months, current_savings)

        # Calculate percentage of income
        income_percentage = (monthly_needed / income * 100) if income > 0 else 0

        # Create plan
        plan = {
            "goal_name": goal_name,
            "target_amount": target_amount,
            "current_savings": current_savings,
            "remaining_amount": target_amount - current_savings,
            "months": months,
            "monthly_savings_needed": monthly_needed,
            "percentage_of_income": round(income_percentage, 2)
        }

        # Build AI prompt
        persona_context = _get_persona_context(persona)

        prompt = f"""You are a financial planning advisor. Create a motivational and actionable savings plan.

{persona_context}

Goal Details:
- Goal: {goal_name}
- Target Amount: {format_currency(target_amount)}
- Current Savings: {format_currency(current_savings)}
- Timeline: {months} months
- Monthly Income: {format_currency(income)}
- Required Monthly Saving: {format_currency(monthly_needed)} ({income_percentage:.1f}% of income)

Provide:
1. Brief assessment of goal feasibility
2. 2-3 specific strategies to reach this goal
3. Motivational encouragement

Keep it concise and actionable (under 150 words)."""

        # Generate advice using AI
        advice = generate(prompt, max_new_tokens=200, temperature=0.7)

        logger.info(f"Goal plan created successfully for: {goal_name}")

        return {
            "plan": plan,
            "advice": advice.strip()
        }

    except Exception as e:
        logger.error(f"Goal planning failed: {str(e)}")
        # Return fallback advice
        return {
            "plan": plan,
            "advice": _get_fallback_advice(goal_name, monthly_needed, income_percentage)
        }


def _get_persona_context(persona: str) -> str:
    """Get context based on user persona"""
    contexts = {
        "student": "The user is a student. Focus on achievable small steps and building habits.",
        "professional": "The user is a working professional. Focus on strategic planning and optimization.",
        "general": "Provide practical financial planning advice."
    }
    return contexts.get(persona.lower(), contexts["general"])


def _get_fallback_advice(goal_name: str, monthly_needed: float, income_percentage: float) -> str:
    """Generate fallback advice when AI fails"""
    if income_percentage > 50:
        return f"""Your goal of {goal_name} is ambitious. You'll need to save {format_currency(monthly_needed)} monthly ({income_percentage:.1f}% of income).

Consider:
- Extending the timeline to make it more manageable
- Finding additional income sources
- Breaking the goal into smaller milestones

Start with what you can save today and increase gradually."""

    elif income_percentage > 30:
        return f"""Your goal of {goal_name} is achievable with discipline. You'll need to save {format_currency(monthly_needed)} monthly.

Strategies:
- Automate your savings on payday
- Cut one major expense category
- Track your progress weekly

Stay consistent and you'll reach your goal!"""

    else:
        return f"""Your goal of {goal_name} is very achievable! You only need to save {format_currency(monthly_needed)} monthly ({income_percentage:.1f}% of income).

Tips:
- Set up automatic transfers to a separate savings account
- Treat this savings as a non-negotiable expense
- Celebrate milestones along the way

You've got this!"""
