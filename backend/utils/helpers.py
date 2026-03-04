"""
Helper utilities for AI Financial Advisor.
Contains common utility functions used across the application.
"""

import json
from typing import Any, Dict, Union
from datetime import datetime


def format_currency(amount: float, currency: str = 'INR') -> str:
    """
    Format a number as currency string.
    
    Args:
        amount: The amount to format
        currency: Currency code (default: INR)
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_currency(50000)
        '₹50,000.00'
    """
    symbols = {
        'INR': '₹',
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    symbol = symbols.get(currency, '₹')
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal as percentage string.
    
    Args:
        value: Decimal value (e.g., 0.25 for 25%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
        
    Example:
        >>> format_percentage(0.25)
        '25.0%'
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    monthly_contribution: float = 0
) -> Dict[str, float]:
    """
    Calculate compound interest with optional monthly contributions.
    
    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate (decimal)
        years: Number of years
        monthly_contribution: Monthly contribution amount (optional)
        
    Returns:
        Dictionary with final amount, total contributions, and interest earned
    """
    monthly_rate = annual_rate / 12
    months = years * 12
    
    # Future value of principal
    fv_principal = principal * ((1 + monthly_rate) ** months)
    
    # Future value of contributions
    if monthly_contribution > 0 and monthly_rate > 0:
        fv_contributions = monthly_contribution * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        ) * (1 + monthly_rate)
    else:
        fv_contributions = monthly_contribution * months
    
    total_value = fv_principal + fv_contributions
    total_contributions = principal + (monthly_contribution * months)
    interest_earned = total_value - total_contributions
    
    return {
        'final_amount': round(total_value, 2),
        'total_contributions': round(total_contributions, 2),
        'interest_earned': round(interest_earned, 2),
        'return_percentage': round((interest_earned / total_contributions) * 100, 2) if total_contributions > 0 else 0
    }


def validate_positive_number(value: Any, field_name: str) -> Union[float, None]:
    """
    Validate that a value is a positive number.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Float value if valid, None otherwise
        
    Raises:
        ValueError: If value is not a positive number
    """
    try:
        num = float(value)
        if num < 0:
            raise ValueError(f"{field_name} must be a positive number")
        return num
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number")


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data by removing potentially harmful characters.
    
    Args:
        data: Dictionary containing input data
        
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially harmful characters
            sanitized[key] = value.strip().replace('<', '').replace('>', '')
        else:
            sanitized[key] = value
    return sanitized


def get_risk_color(risk_level: str) -> str:
    """
    Get color code for risk level.
    
    Args:
        risk_level: Risk level string (Low, Moderate, High)
        
    Returns:
        Hex color code
    """
    colors = {
        'Low': '#28a745',      # Green
        'Moderate': '#ffc107',  # Yellow
        'High': '#dc3545'       # Red
    }
    return colors.get(risk_level, '#6c757d')  # Default gray


def get_health_score_color(score: float) -> str:
    """
    Get color code for financial health score.
    
    Args:
        score: Financial health score (0-100)
        
    Returns:
        Hex color code
    """
    if score >= 80:
        return '#28a745'  # Green
    elif score >= 60:
        return '#17a2b8'  # Blue
    elif score >= 40:
        return '#ffc107'  # Yellow
    elif score >= 20:
        return '#fd7e14'  # Orange
    else:
        return '#dc3545'  # Red


def generate_timeline_labels(years: int) -> list[str]:
    """
    Generate year labels for charts.
    
    Args:
        years: Number of years
        
    Returns:
        List of year labels
    """
    current_year = datetime.now().year
    return [str(current_year + i) for i in range(years + 1)]


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON string.
    
    Args:
        data: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_emergency_fund_target(
    monthly_expenses: float,
    months: int = 6,
    dependents: int = 0
) -> float:
    """
    Calculate recommended emergency fund target.
    
    Args:
        monthly_expenses: Monthly expenses
        months: Base number of months (default: 6)
        dependents: Number of dependents
        
    Returns:
        Recommended emergency fund amount
    """
    # Add 1 month per dependent
    target_months = months + (dependents * 1)
    return monthly_expenses * target_months
