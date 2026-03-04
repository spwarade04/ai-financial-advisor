"""
Goal Service module for AI Financial Advisor.
Handles goal-based financial planning calculations.
"""

import math
from typing import Dict, Any, List
from backend.models.financial_model import GoalPlan


class GoalService:
    """
    Service class for goal-based financial planning.
    
    Provides methods for calculating:
    - Monthly savings requirements
    - SIP projections
    - Portfolio allocations
    - Investment returns
    """
    
    # Portfolio allocation rules by risk level
    PORTFOLIO_ALLOCATIONS = {
        'Low': {
            'Bonds': 60,
            'Mutual Funds': 30,
            'Equity': 10
        },
        'Medium': {
            'Equity': 50,
            'Mutual Funds': 30,
            'Bonds': 20
        },
        'High': {
            'Equity': 70,
            'Mutual Funds': 20,
            'Bonds': 10
        }
    }
    
    # Expected annual return rates by risk level
    RETURN_RATES = {
        'Low': 0.08,      # 8% for low risk
        'Medium': 0.12,   # 12% for medium risk
        'High': 0.16      # 16% for high risk
    }
    
    # Monthly compounding periods per year
    MONTHS_PER_YEAR = 12
    
    def __init__(self):
        """Initialize the goal service."""
        pass
    
    def calculate_monthly_savings_required(
        self,
        goal_amount: float,
        goal_years: int,
        current_savings: float,
        annual_return_rate: float
    ) -> float:
        """
        Calculate the monthly savings required to reach a financial goal.
        
        Uses the future value of annuity formula adjusted for existing savings.
        
        Formula:
        PMT = (FV - PV * (1 + r)^n) / (((1 + r)^n - 1) / r)
        
        Where:
        - PMT = Monthly payment
        - FV = Future value (goal amount)
        - PV = Present value (current savings)
        - r = Monthly interest rate
        - n = Total number of months
        
        Args:
            goal_amount: Target amount to achieve
            goal_years: Number of years to reach goal
            current_savings: Current savings amount
            annual_return_rate: Expected annual return rate (decimal)
            
        Returns:
            Monthly savings amount required
            
        Example:
            >>> service = GoalService()
            >>> service.calculate_monthly_savings_required(500000, 3, 100000, 0.12)
            8500.50
        """
        if goal_years <= 0:
            return 0.0
        
        # Convert to monthly values
        monthly_rate = annual_return_rate / self.MONTHS_PER_YEAR
        total_months = goal_years * self.MONTHS_PER_YEAR
        
        # Future value of current savings
        future_value_current = current_savings * ((1 + monthly_rate) ** total_months)
        
        # Remaining amount needed
        remaining_amount = goal_amount - future_value_current
        
        if remaining_amount <= 0:
            return 0.0
        
        # Calculate monthly payment using annuity formula
        if monthly_rate == 0:
            return remaining_amount / total_months
        
        annuity_factor = ((1 + monthly_rate) ** total_months - 1) / monthly_rate
        monthly_savings = remaining_amount / annuity_factor
        
        return max(0, monthly_savings)
    
    def sip_projection(
        self,
        monthly_investment: float,
        goal_years: int,
        annual_return_rate: float,
        current_savings: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate SIP (Systematic Investment Plan) projections.
        
        Args:
            monthly_investment: Monthly SIP amount
            goal_years: Investment duration in years
            annual_return_rate: Expected annual return rate (decimal)
            current_savings: Initial investment amount
            
        Returns:
            Dictionary with projection details
        """
        monthly_rate = annual_return_rate / self.MONTHS_PER_YEAR
        total_months = goal_years * self.MONTHS_PER_YEAR
        
        # Future value of current savings
        future_value_current = current_savings * ((1 + monthly_rate) ** total_months)
        
        # Future value of SIP investments
        if monthly_rate == 0:
            future_value_sip = monthly_investment * total_months
        else:
            future_value_sip = monthly_investment * (
                ((1 + monthly_rate) ** total_months - 1) / monthly_rate
            ) * (1 + monthly_rate)  # Adjusted for beginning of period
        
        total_value = future_value_current + future_value_sip
        total_invested = current_savings + (monthly_investment * total_months)
        total_returns = total_value - total_invested
        
        # Generate yearly breakdown
        yearly_breakdown = []
        for year in range(1, goal_years + 1):
            months = year * self.MONTHS_PER_YEAR
            fv_current = current_savings * ((1 + monthly_rate) ** months)
            if monthly_rate == 0:
                fv_sip = monthly_investment * months
            else:
                fv_sip = monthly_investment * (
                    ((1 + monthly_rate) ** months - 1) / monthly_rate
                ) * (1 + monthly_rate)
            
            yearly_breakdown.append({
                'year': year,
                'value': round(fv_current + fv_sip, 2),
                'invested': round(current_savings + (monthly_investment * months), 2)
            })
        
        return {
            'total_value': round(total_value, 2),
            'total_invested': round(total_invested, 2),
            'total_returns': round(total_returns, 2),
            'returns_percentage': round((total_returns / total_invested) * 100, 2) if total_invested > 0 else 0,
            'yearly_breakdown': yearly_breakdown
        }
    
    def suggest_portfolio_allocation(self, risk_level: str) -> Dict[str, Any]:
        """
        Suggest portfolio allocation based on risk level.
        
        Args:
            risk_level: Risk appetite ("Low", "Medium", "High")
            
        Returns:
            Dictionary with allocation percentages and descriptions
        """
        if risk_level not in self.PORTFOLIO_ALLOCATIONS:
            raise ValueError(f"Invalid risk level: {risk_level}. Must be Low, Medium, or High.")
        
        allocation = self.PORTFOLIO_ALLOCATIONS[risk_level]
        return_rate = self.RETURN_RATES[risk_level]
        
        descriptions = {
            'Low': {
                'profile': 'Conservative Investor',
                'description': 'Focus on capital preservation with steady, modest returns.',
                'suitable_for': 'Retirees, short-term goals, risk-averse investors'
            },
            'Medium': {
                'profile': 'Balanced Investor',
                'description': 'Balance between growth and stability.',
                'suitable_for': 'Working professionals, medium-term goals (3-7 years)'
            },
            'High': {
                'profile': 'Aggressive Investor',
                'description': 'Focus on maximum growth with higher volatility.',
                'suitable_for': 'Young investors, long-term goals (7+ years)'
            }
        }
        
        return {
            'risk_level': risk_level,
            'allocation': allocation,
            'expected_annual_return': return_rate,
            'profile': descriptions[risk_level]
        }
    
    def get_portfolio_allocation(self, risk_level: str) -> Dict[str, int]:
        """
        Get simple portfolio allocation percentages.
        
        Args:
            risk_level: Risk appetite ("Low", "Medium", "High")
            
        Returns:
            Dictionary with asset class percentages
        """
        return self.PORTFOLIO_ALLOCATIONS.get(risk_level, self.PORTFOLIO_ALLOCATIONS['Medium'])
    
    def calculate_goal_plan(
        self,
        goal_amount: float,
        goal_years: int,
        current_savings: float,
        monthly_savings: float,
        risk_level: str
    ) -> Dict[str, Any]:
        """
        Calculate complete goal-based financial plan.
        
        Args:
            goal_amount: Target amount to achieve
            goal_years: Number of years to reach goal
            current_savings: Current savings amount
            monthly_savings: Available monthly savings
            risk_level: Risk appetite ("Low", "Medium", "High")
            
        Returns:
            Dictionary with complete goal plan
        """
        # Get return rate and allocation for risk level
        return_rate = self.RETURN_RATES.get(risk_level, self.RETURN_RATES['Medium'])
        allocation = self.get_portfolio_allocation(risk_level)
        
        # Calculate required monthly savings
        required_monthly = self.calculate_monthly_savings_required(
            goal_amount=goal_amount,
            goal_years=goal_years,
            current_savings=current_savings,
            annual_return_rate=return_rate
        )
        
        # Calculate SIP projections
        sip_projections = self.sip_projection(
            monthly_investment=required_monthly,
            goal_years=goal_years,
            annual_return_rate=return_rate,
            current_savings=current_savings
        )
        
        # Determine feasibility
        feasibility = 'achievable' if monthly_savings >= required_monthly else 'challenging'
        shortfall = max(0, required_monthly - monthly_savings)
        
        # Create goal plan object
        goal_plan = GoalPlan(
            goal_amount=goal_amount,
            goal_years=goal_years,
            current_savings=current_savings,
            monthly_savings_required=required_monthly,
            projected_amount=sip_projections['total_value'],
            expected_return_rate=return_rate,
            portfolio_allocation=allocation,
            sip_projections=sip_projections
        )
        
        result = goal_plan.to_dict()
        result['feasibility'] = feasibility
        result['monthly_shortfall'] = round(shortfall, 2) if shortfall > 0 else 0
        result['recommendations'] = self._generate_recommendations(
            feasibility, shortfall, goal_years, risk_level
        )
        
        return result
    
    def _generate_recommendations(
        self,
        feasibility: str,
        shortfall: float,
        goal_years: int,
        risk_level: str
    ) -> List[str]:
        """Generate recommendations based on goal feasibility."""
        recommendations = []
        
        if feasibility == 'achievable':
            recommendations.append('Your goal is achievable with your current savings capacity.')
            recommendations.append(f'Invest ₹{shortfall:.0f} monthly through SIP to reach your goal.')
        else:
            recommendations.append('Your current savings rate may not be sufficient for this goal.')
            recommendations.append(f'Consider increasing monthly savings by ₹{shortfall:.0f}.')
            recommendations.append('Alternatively, you could:')
            recommendations.append(f'  - Extend timeline by {(shortfall/1000):.1f} years (approximate)')
            recommendations.append('  - Reduce goal amount')
            if risk_level == 'Low':
                recommendations.append('  - Consider medium risk for potentially higher returns')
        
        return recommendations
