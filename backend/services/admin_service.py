"""
Admin Service.
Provides administrative functions and analytics.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.models.user_model import User, db
from backend.models.financial_record_model import FinancialRecord
from backend.models.goal_model import Goal


@dataclass
class RiskDistribution:
    """Risk level distribution."""
    critical: int
    high: int
    medium: int
    low: int
    
    @property
    def total(self) -> int:
        return self.critical + self.high + self.medium + self.low
    
    def to_dict(self) -> Dict[str, Any]:
        total = self.total
        return {
            'critical': self.critical,
            'high': self.high,
            'medium': self.medium,
            'low': self.low,
            'total': total,
            'percentages': {
                'critical': round(self.critical / total * 100, 2) if total > 0 else 0,
                'high': round(self.high / total * 100, 2) if total > 0 else 0,
                'medium': round(self.medium / total * 100, 2) if total > 0 else 0,
                'low': round(self.low / total * 100, 2) if total > 0 else 0
            }
        }


@dataclass
class SystemAnalytics:
    """System-wide analytics."""
    total_users: int
    active_users_30d: int
    new_users_7d: int
    total_goals: int
    completed_goals: int
    average_savings_rate: float
    average_dti: float
    risk_distribution: RiskDistribution


class AdminService:
    """
    Service for administrative operations and analytics.
    """
    
    @classmethod
    def get_all_users(
        cls,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of all users.
        
        Args:
            page: Page number
            per_page: Items per page
            search: Optional search term
            
        Returns:
            Paginated user list
        """
        query = User.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) | 
                (User.email.ilike(search_term))
            )
        
        # Order by most recent
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'users': [user.to_dict() for user in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    @classmethod
    def get_user_details(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            User details or None
        """
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Get latest financial record
        latest_record = FinancialRecord.query.filter_by(
            user_id=user_id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        # Get goals summary
        goals_summary = db.session.query(
            Goal.status,
            func.count(Goal.id).label('count')
        ).filter_by(user_id=user_id).group_by(Goal.status).all()
        
        goals_count = {status: count for status, count in goals_summary}
        
        return {
            'user': user.to_dict(include_sensitive=True),
            'financial_summary': latest_record.to_dict() if latest_record else None,
            'goals_summary': {
                'total': sum(goals_count.values()),
                'by_status': goals_count
            }
        }
    
    @classmethod
    def get_risk_summary(cls) -> Dict[str, Any]:
        """
        Get system-wide risk summary.
        
        Returns:
            Risk summary data
        """
        # Get all latest financial records
        subquery = db.session.query(
            FinancialRecord.user_id,
            func.max(FinancialRecord.record_date).label('max_date')
        ).group_by(FinancialRecord.user_id).subquery()
        
        latest_records = FinancialRecord.query.join(
            subquery,
            db.and_(
                FinancialRecord.user_id == subquery.c.user_id,
                FinancialRecord.record_date == subquery.c.max_date
            )
        ).all()
        
        # Calculate risk distribution
        critical = high = medium = low = 0
        savings_rates = []
        dtis = []
        
        for record in latest_records:
            # Determine risk level
            if record.emergency_fund_status == 'Critical' or record.dti_ratio > 50:
                critical += 1
            elif record.emergency_fund_status == 'Moderate' or record.dti_ratio > 30:
                high += 1
            elif record.savings_rate < 10 or record.dti_ratio > 20:
                medium += 1
            else:
                low += 1
            
            savings_rates.append(record.savings_rate)
            dtis.append(record.dti_ratio)
        
        risk_distribution = RiskDistribution(
            critical=critical,
            high=high,
            medium=medium,
            low=low
        )
        
        # Calculate averages
        avg_savings = sum(savings_rates) / len(savings_rates) if savings_rates else 0
        avg_dti = sum(dtis) / len(dtis) if dtis else 0
        
        return {
            'total_users_analyzed': len(latest_records),
            'risk_distribution': risk_distribution.to_dict(),
            'average_metrics': {
                'savings_rate': round(avg_savings, 2),
                'dti_ratio': round(avg_dti, 2)
            },
            'health_score': cls._calculate_health_score(risk_distribution)
        }
    
    @classmethod
    def get_system_analytics(cls) -> SystemAnalytics:
        """
        Get comprehensive system analytics.
        
        Returns:
            SystemAnalytics object
        """
        # User statistics
        total_users = User.query.count()
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users_30d = User.query.filter(
            User.last_login >= thirty_days_ago
        ).count()
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_users_7d = User.query.filter(
            User.created_at >= seven_days_ago
        ).count()
        
        # Goal statistics
        total_goals = Goal.query.count()
        completed_goals = Goal.query.filter_by(status='completed').count()
        
        # Get risk summary for averages
        risk_summary = cls.get_risk_summary()
        avg_metrics = risk_summary.get('average_metrics', {})
        
        # Build risk distribution from summary
        risk_dist_data = risk_summary.get('risk_distribution', {})
        risk_distribution = RiskDistribution(
            critical=risk_dist_data.get('critical', 0),
            high=risk_dist_data.get('high', 0),
            medium=risk_dist_data.get('medium', 0),
            low=risk_dist_data.get('low', 0)
        )
        
        return SystemAnalytics(
            total_users=total_users,
            active_users_30d=active_users_30d,
            new_users_7d=new_users_7d,
            total_goals=total_goals,
            completed_goals=completed_goals,
            average_savings_rate=avg_metrics.get('savings_rate', 0),
            average_dti=avg_metrics.get('dti_ratio', 0),
            risk_distribution=risk_distribution
        )
    
    @classmethod
    def _calculate_health_score(cls, risk_distribution: RiskDistribution) -> Dict[str, Any]:
        """
        Calculate overall financial health score.
        
        Args:
            risk_distribution: Risk distribution data
            
        Returns:
            Health score information
        """
        total = risk_distribution.total
        if total == 0:
            return {'score': 0, 'rating': 'N/A'}
        
        # Weighted score calculation
        score = (
            risk_distribution.low * 100 +
            risk_distribution.medium * 75 +
            risk_distribution.high * 50 +
            risk_distribution.critical * 25
        ) / total
        
        # Determine rating
        if score >= 80:
            rating = 'Excellent'
        elif score >= 60:
            rating = 'Good'
        elif score >= 40:
            rating = 'Fair'
        else:
            rating = 'Poor'
        
        return {
            'score': round(score, 2),
            'rating': rating,
            'max_score': 100
        }
    
    @classmethod
    def to_dict_analytics(cls, analytics: SystemAnalytics) -> Dict[str, Any]:
        """
        Convert analytics to dictionary.
        
        Args:
            analytics: SystemAnalytics object
            
        Returns:
            Dictionary representation
        """
        return {
            'users': {
                'total': analytics.total_users,
                'active_30d': analytics.active_users_30d,
                'new_7d': analytics.new_users_7d
            },
            'goals': {
                'total': analytics.total_goals,
                'completed': analytics.completed_goals,
                'completion_rate': round(
                    analytics.completed_goals / analytics.total_goals * 100, 2
                ) if analytics.total_goals > 0 else 0
            },
            'financial_health': {
                'average_savings_rate': analytics.average_savings_rate,
                'average_dti': analytics.average_dti,
                'risk_distribution': analytics.risk_distribution.to_dict()
            }
        }
