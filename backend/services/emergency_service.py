"""
Emergency Fund Analyzer Service.
Analyzes emergency fund status and provides recommendations.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from backend.models.financial_record_model import FinancialRecord


@dataclass
class EmergencyFundAnalysis:
    """Emergency fund analysis result."""
    current_amount: float
    target_amount: float
    progress_percentage: float
    status: str
    monthly_expenses: float
    months_covered: float
    recommendation: str
    priority_actions: list


class EmergencyFundService:
    """
    Service for analyzing emergency fund status.
    """
    
    # Status thresholds
    CRITICAL_THRESHOLD = 40.0
    MODERATE_THRESHOLD = 80.0
    
    # Target months of expenses
    TARGET_MONTHS = 6
    
    @classmethod
    def analyze(cls, financial_record: FinancialRecord) -> EmergencyFundAnalysis:
        """
        Analyze emergency fund status.
        
        Args:
            financial_record: User's financial record
            
        Returns:
            EmergencyFundAnalysis with detailed assessment
        """
        monthly_expenses = financial_record.monthly_expenses
        current_fund = financial_record.emergency_fund_amount
        target_amount = monthly_expenses * cls.TARGET_MONTHS
        
        # Calculate progress
        if target_amount > 0:
            progress_percentage = (current_fund / target_amount) * 100
        else:
            progress_percentage = 0.0
        
        # Determine status
        status = cls._determine_status(progress_percentage)
        
        # Calculate months covered
        if monthly_expenses > 0:
            months_covered = current_fund / monthly_expenses
        else:
            months_covered = 0.0
        
        # Generate recommendation
        recommendation = cls._generate_recommendation(
            progress_percentage, current_fund, target_amount, monthly_expenses
        )
        
        # Generate priority actions
        priority_actions = cls._generate_priority_actions(
            status, current_fund, monthly_expenses, financial_record
        )
        
        return EmergencyFundAnalysis(
            current_amount=current_fund,
            target_amount=target_amount,
            progress_percentage=round(progress_percentage, 2),
            status=status,
            monthly_expenses=monthly_expenses,
            months_covered=round(months_covered, 1),
            recommendation=recommendation,
            priority_actions=priority_actions
        )
    
    @classmethod
    def _determine_status(cls, progress_percentage: float) -> str:
        """
        Determine emergency fund status based on progress.
        
        Args:
            progress_percentage: Current progress percentage
            
        Returns:
            Status string: 'Critical', 'Moderate', or 'Safe'
        """
        if progress_percentage < cls.CRITICAL_THRESHOLD:
            return 'Critical'
        elif progress_percentage < cls.MODERATE_THRESHOLD:
            return 'Moderate'
        return 'Safe'
    
    @classmethod
    def _generate_recommendation(
        cls,
        progress_percentage: float,
        current_fund: float,
        target_amount: float,
        monthly_expenses: float
    ) -> str:
        """
        Generate personalized recommendation.
        
        Args:
            progress_percentage: Current progress percentage
            current_fund: Current emergency fund amount
            target_amount: Target emergency fund amount
            monthly_expenses: Monthly expenses
            
        Returns:
            Recommendation string
        """
        if progress_percentage < cls.CRITICAL_THRESHOLD:
            gap = target_amount - current_fund
            months_to_target = gap / (monthly_expenses * 0.2) if monthly_expenses > 0 else 0
            
            return (
                f"Your emergency fund is at CRITICAL levels ({progress_percentage:.1f}% of target). "
                f"You need ₹{gap:,.2f} more to reach a safe 6-month cushion. "
                f"Consider aggressively saving 20% of your income to reach the target in {months_to_target:.1f} months. "
                f"Immediate action required to protect against unexpected expenses."
            )
        
        elif progress_percentage < cls.MODERATE_THRESHOLD:
            gap = target_amount - current_fund
            
            return (
                f"Your emergency fund is at MODERATE levels ({progress_percentage:.1f}% of target). "
                f"You need ₹{gap:,.2f} more for complete security. "
                f"Continue building your fund with consistent monthly contributions. "
                f"Aim to reach 100% within the next 6-12 months."
            )
        
        else:
            excess = current_fund - target_amount
            
            if excess > 0:
                return (
                    f"Excellent! Your emergency fund is at SAFE levels ({progress_percentage:.1f}% of target). "
                    f"You have ₹{excess:,.2f} above the recommended 6-month cushion. "
                    f"Consider investing the excess in higher-yield instruments while maintaining your safety net."
                )
            else:
                return (
                    f"Great job! Your emergency fund is at SAFE levels ({progress_percentage:.1f}% of target). "
                    f"You have a solid 6-month expense cushion. Maintain this fund and focus on other financial goals."
                )
    
    @classmethod
    def _generate_priority_actions(
        cls,
        status: str,
        current_fund: float,
        monthly_expenses: float,
        financial_record: FinancialRecord
    ) -> list:
        """
        Generate priority action items.
        
        Args:
            status: Current status
            current_fund: Current emergency fund
            monthly_expenses: Monthly expenses
            financial_record: Full financial record
            
        Returns:
            List of priority actions
        """
        actions = []
        
        if status == 'Critical':
            actions.extend([
                "Set up automatic transfer of 15-20% of income to emergency fund",
                "Reduce non-essential expenses immediately",
                "Consider temporary additional income sources",
                "Keep emergency fund in high-yield savings account",
                "Avoid new debt until fund reaches at least 3 months of expenses"
            ])
        
        elif status == 'Moderate':
            actions.extend([
                "Maintain automatic monthly contributions to emergency fund",
                "Review and optimize monthly budget for faster growth",
                "Consider keeping 3 months in savings, remainder in liquid funds",
                "Track progress monthly and adjust contributions as needed"
            ])
        
        else:  # Safe
            actions.extend([
                "Continue monitoring emergency fund level quarterly",
                "Consider investing excess above 6-month target",
                "Review emergency fund if monthly expenses increase significantly",
                "Maintain fund in easily accessible accounts"
            ])
        
        # Add specific recommendation based on savings rate
        savings_rate = financial_record.savings_rate
        if savings_rate < 10:
            actions.insert(0, f"CRITICAL: Your savings rate ({savings_rate:.1f}%) is too low. Increase immediately.")
        elif savings_rate < 20:
            actions.insert(0, f"Consider increasing savings rate from {savings_rate:.1f}% to 20% for faster growth.")
        
        return actions
    
    @classmethod
    def to_dict(cls, analysis: EmergencyFundAnalysis) -> Dict[str, Any]:
        """
        Convert analysis to dictionary.
        
        Args:
            analysis: EmergencyFundAnalysis object
            
        Returns:
            Dictionary representation
        """
        return {
            'current_amount': analysis.current_amount,
            'target_amount': analysis.target_amount,
            'progress_percentage': analysis.progress_percentage,
            'status': analysis.status,
            'monthly_expenses': analysis.monthly_expenses,
            'months_covered': analysis.months_covered,
            'recommendation': analysis.recommendation,
            'priority_actions': analysis.priority_actions
        }
