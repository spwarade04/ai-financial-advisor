"""
Goal model for storing user financial goals.
"""

from datetime import datetime
from backend.models.user_model import db


class Goal(db.Model):
    """
    Goal model for storing and tracking financial goals.
    """
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Goal details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    
    # Timeline
    target_date = db.Column(db.DateTime, nullable=True)
    
    # Goal type
    goal_type = db.Column(db.String(50), default='savings')  # savings, investment, debt_repayment, purchase
    
    # Monthly contribution
    monthly_contribution = db.Column(db.Float, default=0.0)
    
    # Expected return rate (for investment goals)
    expected_return_rate = db.Column(db.Float, default=0.0)  # Annual rate as decimal
    
    # Priority
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, paused, cancelled
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id: int, name: str, target_amount: float, **kwargs):
        """
        Initialize a new goal.
        
        Args:
            user_id: ID of the user this goal belongs to
            name: Name of the goal
            target_amount: Target amount to achieve
            **kwargs: Additional goal fields
        """
        self.user_id = user_id
        self.name = name
        self.target_amount = target_amount
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate goal progress percentage."""
        if self.target_amount == 0:
            return 0.0
        return (self.current_amount / self.target_amount) * 100
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach goal."""
        return max(0, self.target_amount - self.current_amount)
    
    @property
    def projected_completion_date(self) -> datetime:
        """
        Calculate projected completion date based on monthly contribution.
        
        Returns:
            Projected completion date or None if cannot be calculated
        """
        if self.monthly_contribution <= 0:
            return None
        
        months_needed = self.remaining_amount / self.monthly_contribution
        return datetime.utcnow().replace(day=1) + __import__('dateutil.relativedelta', fromlist=['relativedelta']).relativedelta(months=int(months_needed) + 1)
    
    @property
    def is_on_track(self) -> bool:
        """Check if goal is on track to be completed by target date."""
        if not self.target_date:
            return True
        
        projected = self.projected_completion_date
        if not projected:
            return False
        
        return projected <= self.target_date
    
    def complete(self):
        """Mark goal as completed."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.current_amount = self.target_amount
    
    def to_dict(self) -> dict:
        """
        Convert goal to dictionary.
        
        Returns:
            Goal data as dictionary
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'remaining_amount': self.remaining_amount,
            'progress_percentage': round(self.progress_percentage, 2),
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'projected_completion': self.projected_completion_date.isoformat() if self.projected_completion_date else None,
            'goal_type': self.goal_type,
            'monthly_contribution': self.monthly_contribution,
            'expected_return_rate': self.expected_return_rate,
            'priority': self.priority,
            'status': self.status,
            'is_on_track': self.is_on_track,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Goal {self.name} user_id={self.user_id}>'
