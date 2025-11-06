"""
Intent Router
Routes user queries to appropriate agents based on keywords
"""
from core.logger import logger


def route_intent(query: str) -> str:
    """
    Determine which agent should handle the query

    Args:
        query: User's question or intent

    Returns:
        str: Agent name ('budget', 'goal', 'tax', 'general')
    """
    query_lower = query.lower()

    # Goal-related keywords
    goal_keywords = ['goal', 'save', 'saving', 'target', 'plan', 'planning', 'achieve', 'buy', 'purchase']
    if any(keyword in query_lower for keyword in goal_keywords):
        logger.info(f"Routing to goal_agent: {query[:50]}")
        return 'goal'

    # Tax-related keywords
    tax_keywords = ['tax', 'deduction', 'exemption', '80c', 'itr', 'income tax', 'tax saving']
    if any(keyword in query_lower for keyword in tax_keywords):
        logger.info(f"Routing to tax_agent: {query[:50]}")
        return 'tax'

    # Budget-related keywords
    budget_keywords = ['budget', 'spend', 'spending', 'expense', 'expenses', 'cost', 'money']
    if any(keyword in query_lower for keyword in budget_keywords):
        logger.info(f"Routing to budget_agent: {query[:50]}")
        return 'budget'

    # Default to general
    logger.info(f"Routing to general: {query[:50]}")
    return 'general'


def get_fallback_response(query: str) -> str:
    """
    Generate a fallback response for unrecognized intents

    Args:
        query: User's question

    Returns:
        str: Fallback response
    """
    return """I'm your personal finance assistant. I can help you with:

- **Budget Analysis**: Analyze your spending and provide insights
- **Goal Planning**: Create savings plans for your financial goals
- **Tax Advice**: Get tips on tax-saving investments

Please ask me about budgeting, financial goals, or tax planning, and I'll be happy to help!"""
