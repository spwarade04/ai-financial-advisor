"""
Financial Record model for storing user financial data.
"""

from datetime import datetime
from backend.models.user_model import db


class FinancialRecord(db.Model):
    """
    Financial record model for storing income, expenses, assets, and liabilities.
    """
    __tablename__ = 'financial_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Income
    monthly_income = db.Column(db.Float, nullable=False, default=0.0)
    
    # Expenses breakdown
    monthly_expenses = db.Column(db.Float, nullable=False, default=0.0)
    rent_expense = db.Column(db.Float, default=0.0)
    utilities_expense = db.Column(db.Float, default=0.0)
    groceries_expense = db.Column(db.Float, default=0.0)
    transport_expense = db.Column(db.Float, default=0.0)
    entertainment_expense = db.Column(db.Float, default=0.0)
    other_expenses = db.Column(db.Float, default=0.0)
    
    # Assets
    total_assets = db.Column(db.Float, default=0.0)
    cash_savings = db.Column(db.Float, default=0.0)
    investments = db.Column(db.Float, default=0.0)
    real_estate = db.Column(db.Float, default=0.0)
    other_assets = db.Column(db.Float, default=0.0)
    
    # Liabilities
    total_liabilities = db.Column(db.Float, default=0.0)
    credit_card_debt = db.Column(db.Float, default=0.0)
    student_loans = db.Column(db.Float, default=0.0)
    personal_loans = db.Column(db.Float, default=0.0)
    mortgage = db.Column(db.Float, default=0.0)
    other_liabilities = db.Column(db.Float, default=0.0)
    
    # Emergency Fund
    emergency_fund_amount = db.Column(db.Float, default=0.0)
    
    # Metadata
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id: int, **kwargs):
        """
        Initialize a new financial record.
        
        Args:
            user_id: ID of the user this record belongs to
            **kwargs: Financial data fields
        """
        self.user_id = user_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, float(value) if value is not None else 0.0)
    
    @property
    def net_worth(self) -> float:
        """Calculate net worth (assets - liabilities)."""
        return self.total_assets - self.total_liabilities
    
    @property
    def emergency_fund_target(self) -> float:
        """Calculate emergency fund target (6 months of expenses)."""
        return self.monthly_expenses * 6
    
    @property
    def emergency_fund_progress(self) -> float:
        """Calculate emergency fund progress percentage."""
        target = self.emergency_fund_target
        if target == 0:
            return 0.0
        return (self.emergency_fund_amount / target) * 100
    
    @property
    def emergency_fund_status(self) -> str:
        """Get emergency fund status based on progress."""
        progress = self.emergency_fund_progress
        if progress < 40:
            return 'Critical'
        elif progress < 80:
            return 'Moderate'
        return 'Safe'
    
    @property
    def savings_rate(self) -> float:
        """Calculate savings rate percentage."""
        if self.monthly_income == 0:
            return 0.0
        return ((self.monthly_income - self.monthly_expenses) / self.monthly_income) * 100
    
    @property
    def dti_ratio(self) -> float:
        """Calculate debt-to-income ratio."""
        if self.monthly_income == 0:
            return 0.0
        # Assuming average monthly debt payment is 5% of total liabilities
        monthly_debt_payment = self.total_liabilities * 0.05
        return (monthly_debt_payment / self.monthly_income) * 100
    
    def to_dict(self) -> dict:
        """
        Convert financial record to dictionary.
        
        Returns:
            Financial record data as dictionary
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'income': {
                'monthly_income': self.monthly_income
            },
            'expenses': {
                'monthly_expenses': self.monthly_expenses,
                'rent': self.rent_expense,
                'utilities': self.utilities_expense,
                'groceries': self.groceries_expense,
                'transport': self.transport_expense,
                'entertainment': self.entertainment_expense,
                'other': self.other_expenses
            },
            'assets': {
                'total_assets': self.total_assets,
                'cash_savings': self.cash_savings,
                'investments': self.investments,
                'real_estate': self.real_estate,
                'other': self.other_assets
            },
            'liabilities': {
                'total_liabilities': self.total_liabilities,
                'credit_card': self.credit_card_debt,
                'student_loans': self.student_loans,
                'personal_loans': self.personal_loans,
                'mortgage': self.mortgage,
                'other': self.other_liabilities
            },
            'net_worth': self.net_worth,
            'emergency_fund': {
                'current': self.emergency_fund_amount,
                'target': self.emergency_fund_target,
                'progress_percentage': round(self.emergency_fund_progress, 2),
                'status': self.emergency_fund_status
            },
            'financial_health': {
                'savings_rate': round(self.savings_rate, 2),
                'dti_ratio': round(self.dti_ratio, 2)
            },
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<FinancialRecord user_id={self.user_id} date={self.record_date}>'
