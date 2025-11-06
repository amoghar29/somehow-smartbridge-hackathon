"""
Budget Analysis Agent
Analyzes user spending patterns and provides financial insights
"""
from typing import Dict, Any
from core.granite_api import generate
from core.utils import (
    calculate_total_expenses,
    calc_savings_rate,
    get_top_expenses,
    format_currency
)
from core.logger import logger


def analyze_budget(income: float, expenses: Dict[str, float], persona: str = "general") -> Dict[str, Any]:
    """
    Analyze budget and generate insights using AI

    Args:
        income: Monthly income
        expenses: Dictionary of expense categories and amounts
        persona: User persona (student/professional/general)

    Returns:
        Dict containing summary and insights
    """
    try:
        logger.info(f"Analyzing budget for persona: {persona}")

        # Calculate metrics
        total_expenses = calculate_total_expenses(expenses)
        savings_rate = calc_savings_rate(income, total_expenses)
        top_expenses = get_top_expenses(expenses, n=3)

        # Create summary
        summary = {
            "income": income,
            "total_expenses": total_expenses,
            "savings": income - total_expenses,
            "savings_rate": savings_rate,
            "top_expenses": [
                {"category": cat, "amount": amt} for cat, amt in top_expenses
            ]
        }

        # Build AI prompt based on persona
        persona_context = _get_persona_context(persona)

        prompt = f"""You are a personal finance advisor. Analyze this budget and provide 3-4 short, actionable insights.

{persona_context}

Budget Details:
- Monthly Income: {format_currency(income)}
- Total Expenses: {format_currency(total_expenses)}
- Savings: {format_currency(income - total_expenses)}
- Savings Rate: {savings_rate}%

Top Expense Categories:
{_format_expenses_list(top_expenses)}

Provide 3-4 brief, specific recommendations to improve their financial situation. Keep each point under 20 words."""

        # Generate insights using AI
        ai_response = generate(prompt, max_new_tokens=250, temperature=0.7)

        # Parse insights into a list
        insights = _parse_insights(ai_response)

        logger.info(f"Budget analysis completed with {len(insights)} insights")

        return {
            "summary": summary,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Budget analysis failed: {str(e)}")
        # Return fallback insights
        return {
            "summary": summary,
            "insights": _get_fallback_insights(income, total_expenses, savings_rate, top_expenses)
        }


def _get_persona_context(persona: str) -> str:
    """Get context based on user persona"""
    contexts = {
        "student": "The user is a student with limited income. Focus on budgeting basics and smart spending.",
        "professional": "The user is a working professional. Focus on investment opportunities and wealth building.",
        "general": "Provide general financial advice suitable for most people."
    }
    return contexts.get(persona.lower(), contexts["general"])


def _format_expenses_list(top_expenses) -> str:
    """Format top expenses as a string"""
    return "\n".join([f"- {cat}: {format_currency(amt)}" for cat, amt in top_expenses])


def _parse_insights(ai_response: str) -> list:
    """Parse AI response into a list of insights"""
    # Split by common delimiters
    lines = ai_response.strip().split('\n')
    insights = []

    for line in lines:
        line = line.strip()
        # Remove bullet points, numbers, etc.
        line = line.lstrip('•-*123456789. ')
        if line and len(line) > 10:  # Filter out very short lines
            insights.append(line)

    # If parsing fails, return the whole response
    if not insights:
        insights = [ai_response.strip()]

    return insights[:4]  # Return at most 4 insights


def _get_fallback_insights(income: float, total_expenses: float, savings_rate: float, top_expenses) -> list:
    """Generate fallback insights when AI fails"""
    insights = []

    if savings_rate < 20:
        insights.append(f"Your savings rate is {savings_rate}%. Aim for at least 20% to build financial security.")
    else:
        insights.append(f"Great job! Your savings rate of {savings_rate}% is healthy.")

    if top_expenses:
        top_cat, top_amt = top_expenses[0]
        insights.append(f"Your highest expense is {top_cat} at {format_currency(top_amt)}. Look for ways to optimize this.")

    insights.append("Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings.")

    return insights
