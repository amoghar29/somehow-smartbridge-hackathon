"""
Configuration settings for the Personal Finance Assistant frontend.
"""

import os

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# App configuration
APP_TITLE = "Personal Finance Assistant"
APP_ICON = "💰"

# Currencies supported
CURRENCIES = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€"
}

# Default currency
DEFAULT_CURRENCY = "INR"

# Chart color schemes
CHART_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#84fab0",
    "warning": "#fee140",
    "danger": "#f5576c"
}

# Transaction categories
TRANSACTION_CATEGORIES = [
    "Food & Dining",
    "Shopping",
    "Transportation",
    "Bills & Utilities",
    "Healthcare",
    "Entertainment",
    "Education",
    "Travel",
    "Investments",
    "Other"
]

# Goal categories
GOAL_CATEGORIES = [
    "Travel",
    "Education",
    "Emergency Fund",
    "Home",
    "Car",
    "Retirement",
    "Other"
]

# Time periods for analytics
TIME_PERIODS = ["daily", "weekly", "monthly", "yearly"]
