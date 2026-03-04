"""
Net Worth Tracking Service.
Tracks and analyzes net worth over time.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from backend.models.financial_record_model import FinancialRecord
from backend.models.user_model import db


@dataclass
class NetWorthDataPoint:
    """Single net worth data point."""
    date: datetime
    total_assets: float
    total_liabilities: float
    net_worth: float


@dataclass
class NetWorthAnalysis:
    """Net worth analysis result."""
    current_net_worth: float
    total_assets: float
    total_liabilities: float
    asset_breakdown: Dict[str, float]
    liability_breakdown: Dict[str, float]
    historical_data: List[NetWorthDataPoint]
    growth_rate: float
    monthly_change: float
    yearly_projection: float
    recommendations: List[str]


class NetWorthService:
    """
    Service for tracking and analyzing net worth.
    """
    
    @classmethod
    def analyze(
        cls,
        user_id: int,
        current_record: FinancialRecord,
        months_history: int = 12
    ) -> NetWorthAnalysis:
        """
        Analyze net worth for a user.
        
        Args:
            user_id: User ID
            current_record: Current financial record
            months_history: Number of months of history to retrieve
            
        Returns:
            NetWorthAnalysis with detailed assessment
        """
        # Get historical data
        historical_data = cls._get_historical_data(user_id, months_history)
        
        # Calculate current values
        current_net_worth = current_record.net_worth
        total_assets = current_record.total_assets
        total_liabilities = current_record.total_liabilities
        
        # Asset breakdown
        asset_breakdown = {
            'cash_savings': current_record.cash_savings,
            'investments': current_record.investments,
            'real_estate': current_record.real_estate,
            'other': current_record.other_assets
        }
        
        # Liability breakdown
        liability_breakdown = {
            'credit_card': current_record.credit_card_debt,
            'student_loans': current_record.student_loans,
            'personal_loans': current_record.personal_loans,
            'mortgage': current_record.mortgage,
            'other': current_record.other_liabilities
        }
        
        # Calculate growth metrics
        growth_rate = cls._calculate_growth_rate(historical_data)
        monthly_change = cls._calculate_monthly_change(historical_data)
        
        # Project yearly net worth
        yearly_projection = current_net_worth * ((1 + growth_rate / 100) ** 12) if growth_rate > 0 else current_net_worth
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(
            current_net_worth, total_assets, total_liabilities,
            asset_breakdown, liability_breakdown, growth_rate
        )
        
        return NetWorthAnalysis(
            current_net_worth=current_net_worth,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            asset_breakdown=asset_breakdown,
            liability_breakdown=liability_breakdown,
            historical_data=historical_data,
            growth_rate=round(growth_rate, 2),
            monthly_change=round(monthly_change, 2),
            yearly_projection=round(yearly_projection, 2),
            recommendations=recommendations
        )
    
    @classmethod
    def _get_historical_data(
        cls,
        user_id: int,
        months: int
    ) -> List[NetWorthDataPoint]:
        """
        Retrieve historical net worth data.
        
        Args:
            user_id: User ID
            months: Number of months to retrieve
            
        Returns:
            List of NetWorthDataPoint
        """
        cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
        
        records = FinancialRecord.query.filter(
            FinancialRecord.user_id == user_id,
            FinancialRecord.record_date >= cutoff_date
        ).order_by(FinancialRecord.record_date.asc()).all()
        
        data_points = []
        for record in records:
            data_points.append(NetWorthDataPoint(
                date=record.record_date,
                total_assets=record.total_assets,
                total_liabilities=record.total_liabilities,
                net_worth=record.net_worth
            ))
        
        return data_points
    
    @classmethod
    def _calculate_growth_rate(cls, historical_data: List[NetWorthDataPoint]) -> float:
        """
        Calculate monthly growth rate from historical data.
        
        Args:
            historical_data: List of historical data points
            
        Returns:
            Monthly growth rate percentage
        """
        if len(historical_data) < 2:
            return 0.0
        
        first_value = historical_data[0].net_worth
        last_value = historical_data[-1].net_worth
        months = len(historical_data) - 1
        
        if first_value == 0:
            return 0.0
        
        # Calculate compound monthly growth rate
        growth_rate = ((last_value / first_value) ** (1 / months) - 1) * 100
        return growth_rate
    
    @classmethod
    def _calculate_monthly_change(cls, historical_data: List[NetWorthDataPoint]) -> float:
        """
        Calculate average monthly change.
        
        Args:
            historical_data: List of historical data points
            
        Returns:
            Average monthly change amount
        """
        if len(historical_data) < 2:
            return 0.0
        
        total_change = historical_data[-1].net_worth - historical_data[0].net_worth
        months = len(historical_data) - 1
        
        return total_change / months
    
    @classmethod
    def _generate_recommendations(
        cls,
        net_worth: float,
        assets: float,
        liabilities: float,
        asset_breakdown: Dict[str, float],
        liability_breakdown: Dict[str, float],
        growth_rate: float
    ) -> List[str]:
        """
        Generate personalized recommendations.
        
        Args:
            net_worth: Current net worth
            assets: Total assets
            liabilities: Total liabilities
            asset_breakdown: Breakdown of assets
            liability_breakdown: Breakdown of liabilities
            growth_rate: Monthly growth rate
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Net worth health
        if net_worth < 0:
            recommendations.append(
                "ALERT: Your net worth is negative. Focus on debt reduction immediately."
            )
        elif net_worth < 100000:
            recommendations.append(
                "Your net worth is in early growth stage. Focus on building assets and reducing liabilities."
            )
        else:
            recommendations.append(
                "Your net worth is healthy. Focus on diversification and wealth preservation."
            )
        
        # Asset allocation
        cash_percentage = (asset_breakdown.get('cash_savings', 0) / assets * 100) if assets > 0 else 0
        if cash_percentage > 30:
            recommendations.append(
                f"You have {cash_percentage:.1f}% in cash. Consider investing excess cash for better returns."
            )
        elif cash_percentage < 5:
            recommendations.append(
                f"Your cash reserves are low ({cash_percentage:.1f}%). Build up emergency fund before investing."
            )
        
        # Investment allocation
        investment_percentage = (asset_breakdown.get('investments', 0) / assets * 100) if assets > 0 else 0
        if investment_percentage < 20 and assets > 50000:
            recommendations.append(
                "Consider increasing investment allocation to build long-term wealth."
            )
        
        # Debt analysis
        high_interest_debt = liability_breakdown.get('credit_card', 0) + liability_breakdown.get('personal_loans', 0)
        if high_interest_debt > 0:
            recommendations.append(
                f"Prioritize paying off high-interest debt (₹{high_interest_debt:,.2f}) to improve net worth faster."
            )
        
        # Growth rate
        if growth_rate < 0:
            recommendations.append(
                "Your net worth is declining. Review expenses and increase savings rate immediately."
            )
        elif growth_rate < 1:
            recommendations.append(
                "Your net worth growth is slow. Look for opportunities to increase income or reduce expenses."
            )
        elif growth_rate > 5:
            recommendations.append(
                "Excellent growth rate! Maintain your current financial habits."
            )
        
        # Debt-to-asset ratio
        debt_ratio = (liabilities / assets * 100) if assets > 0 else 0
        if debt_ratio > 50:
            recommendations.append(
                f"Your debt-to-asset ratio is high ({debt_ratio:.1f}%). Focus on debt reduction."
            )
        
        return recommendations
    
    @classmethod
    def to_dict(cls, analysis: NetWorthAnalysis) -> Dict[str, Any]:
        """
        Convert analysis to dictionary.
        
        Args:
            analysis: NetWorthAnalysis object
            
        Returns:
            Dictionary representation
        """
        return {
            'current_net_worth': analysis.current_net_worth,
            'total_assets': analysis.total_assets,
            'total_liabilities': analysis.total_liabilities,
            'asset_breakdown': analysis.asset_breakdown,
            'liability_breakdown': analysis.liability_breakdown,
            'historical_data': [
                {
                    'date': dp.date.isoformat(),
                    'total_assets': dp.total_assets,
                    'total_liabilities': dp.total_liabilities,
                    'net_worth': dp.net_worth
                }
                for dp in analysis.historical_data
            ],
            'growth_rate': analysis.growth_rate,
            'monthly_change': analysis.monthly_change,
            'yearly_projection': analysis.yearly_projection,
            'recommendations': analysis.recommendations
        }
