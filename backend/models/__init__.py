"""
Database models for AI Financial Advisor.
"""

from backend.models.user_model import User, db
from backend.models.financial_record_model import FinancialRecord
from backend.models.goal_model import Goal

__all__ = ['User', 'FinancialRecord', 'Goal', 'db']
