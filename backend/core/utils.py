"""
Utility functions for finance calculations and formatting
"""
from typing import Dict, List, Tuple


def calc_savings_rate(income: float, expenses: float) -> float:
    """
    Calculate savings rate as a percentage

    Args:
        income: Total income
        expenses: Total expenses

    Returns:
        float: Savings rate as percentage (0-100)
    """
    if income <= 0:
        return 0.0

    savings = income - expenses
    savings_rate = (savings / income) * 100

    return round(max(0.0, savings_rate), 2)


def get_top_expenses(expenses_dict: Dict[str, float], n: int = 3) -> List[Tuple[str, float]]:
    """
    Get top N expense categories by amount

    Args:
        expenses_dict: Dictionary of category names to amounts
        n: Number of top categories to return

    Returns:
        List of tuples (category, amount) sorted by amount (highest first)
    """
    if not expenses_dict:
        return []

    # Sort by amount in descending order
    sorted_expenses = sorted(
        expenses_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_expenses[:n]


def format_currency(value: float, symbol: str = "₹") -> str:
    """
    Format a number as currency with Indian Rupee symbol

    Args:
        value: Numeric value to format
        symbol: Currency symbol (default: ₹)

    Returns:
        str: Formatted currency string (e.g., "₹60,000")
    """
    return f"{symbol}{value:,.2f}"


def calculate_total_expenses(expenses_dict: Dict[str, float]) -> float:
    """
    Calculate total expenses from a dictionary of categories

    Args:
        expenses_dict: Dictionary of category names to amounts

    Returns:
        float: Total expenses
    """
    return sum(expenses_dict.values())


def calculate_monthly_savings_needed(
    target_amount: float,
    months: int,
    current_savings: float = 0.0
) -> float:
    """
    Calculate monthly savings needed to reach a goal

    Args:
        target_amount: Target amount to save
        months: Number of months to reach the goal
        current_savings: Current savings amount

    Returns:
        float: Monthly savings required
    """
    if months <= 0:
        return target_amount - current_savings

    remaining_amount = target_amount - current_savings
    monthly_needed = remaining_amount / months

    return round(max(0.0, monthly_needed), 2)


def validate_positive_number(value: float, field_name: str = "value") -> None:
    """
    Validate that a number is positive

    Args:
        value: Number to validate
        field_name: Name of the field for error message

    Raises:
        ValueError: If value is negative
    """
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")


def calculate_expense_percentage(category_amount: float, total_expenses: float) -> float:
    """
    Calculate what percentage a category is of total expenses

    Args:
        category_amount: Amount spent in category
        total_expenses: Total expenses

    Returns:
        float: Percentage (0-100)
    """
    if total_expenses <= 0:
        return 0.0

    percentage = (category_amount / total_expenses) * 100
    return round(percentage, 2)
