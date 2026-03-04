"""
Financial models for AI Financial Advisor.
Defines data structures for financial calculations.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FinancialMetrics:
    """Data class for storing financial metrics."""
    
    # Input values
    income: float
    expenses: float
    savings: float
    debt: float
    
    # Calculated metrics
    monthly_surplus: float
    budget_ratio: float
    savings_rate: float
    debt_to_income_ratio: float
    financial_health_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'income': round(self.income, 2),
            'expenses': round(self.expenses, 2),
            'savings': round(self.savings, 2),
            'debt': round(self.debt, 2),
            'monthly_surplus': round(self.monthly_surplus, 2),
            'budget_ratio': round(self.budget_ratio, 4),
            'savings_rate': round(self.savings_rate, 4),
            'debt_to_income_ratio': round(self.debt_to_income_ratio, 4),
            'financial_health_score': round(self.financial_health_score, 2)
        }


@dataclass
class GoalPlan:
    """Data class for storing goal-based financial plan."""
    
    # Goal parameters
    goal_amount: float
    goal_years: int
    current_savings: float
    
    # Calculated plan
    monthly_savings_required: float
    projected_amount: float
    expected_return_rate: float
    portfolio_allocation: Dict[str, float]
    
    # SIP projections
    sip_projections: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'goal_amount': round(self.goal_amount, 2),
            'goal_years': self.goal_years,
            'current_savings': round(self.current_savings, 2),
            'monthly_savings_required': round(self.monthly_savings_required, 2),
            'projected_amount': round(self.projected_amount, 2),
            'expected_return_rate': round(self.expected_return_rate, 4),
            'portfolio_allocation': self.portfolio_allocation,
            'sip_projections': self.sip_projections
        }


@dataclass
class RiskProfile:
    """Data class for storing risk profile information."""
    
    dti_ratio: float
    classification: str  # "Low", "Moderate", "High"
    description: str
    recommendations: list[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'dti_ratio': round(self.dti_ratio, 4),
            'classification': self.classification,
            'description': self.description,
            'recommendations': self.recommendations
        }
