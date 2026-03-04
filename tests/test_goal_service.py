"""
Unit tests for Goal Service.
Tests all goal planning and SIP calculation methods.
"""

import pytest
import math
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.goal_service import GoalService


class TestGoalService:
    """Test class for GoalService."""
    
    @pytest.fixture
    def service(self):
        """Fixture to create GoalService instance."""
        return GoalService()
    
    def test_calculate_monthly_savings_required_basic(self, service):
        """Test basic monthly savings calculation."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=500000,
            goal_years=3,
            current_savings=100000,
            annual_return_rate=0.12
        )
        
        # Should be a positive number
        assert monthly > 0
        # Should be reasonable (not more than goal amount)
        assert monthly < 500000
    
    def test_calculate_monthly_savings_no_current_savings(self, service):
        """Test calculation with no current savings."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=300000,
            goal_years=2,
            current_savings=0,
            annual_return_rate=0.08
        )
        
        assert monthly > 0
        # Without returns, would need 300000/24 = 12500
        # With 8% returns, should be less
        assert monthly < 12500
    
    def test_calculate_monthly_savings_already_achieved(self, service):
        """Test when current savings already exceed goal."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=100000,
            goal_years=5,
            current_savings=200000,
            annual_return_rate=0.10
        )
        
        assert monthly == 0
    
    def test_calculate_monthly_savings_zero_years(self, service):
        """Test with zero years (edge case)."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=100000,
            goal_years=0,
            current_savings=0,
            annual_return_rate=0.10
        )
        
        assert monthly == 0
    
    def test_sip_projection_basic(self, service):
        """Test basic SIP projection."""
        projection = service.sip_projection(
            monthly_investment=10000,
            goal_years=5,
            annual_return_rate=0.12,
            current_savings=0
        )
        
        # Check structure
        assert 'total_value' in projection
        assert 'total_invested' in projection
        assert 'total_returns' in projection
        assert 'returns_percentage' in projection
        assert 'yearly_breakdown' in projection
        
        # Total invested should be monthly * months
        assert projection['total_invested'] == 10000 * 60
        
        # With positive returns, value should exceed investment
        assert projection['total_value'] > projection['total_invested']
        
        # Returns should be positive
        assert projection['total_returns'] > 0
    
    def test_sip_projection_with_initial(self, service):
        """Test SIP projection with initial investment."""
        projection = service.sip_projection(
            monthly_investment=5000,
            goal_years=3,
            annual_return_rate=0.10,
            current_savings=50000
        )
        
        # Total invested should include initial
        assert projection['total_invested'] == 50000 + (5000 * 36)
    
    def test_sip_projection_zero_return(self, service):
        """Test SIP projection with zero return rate."""
        projection = service.sip_projection(
            monthly_investment=10000,
            goal_years=2,
            annual_return_rate=0,
            current_savings=0
        )
        
        # Without returns, value equals investment
        assert projection['total_value'] == projection['total_invested']
        assert projection['total_returns'] == 0
    
    def test_suggest_portfolio_allocation_low(self, service):
        """Test portfolio allocation for low risk."""
        result = service.suggest_portfolio_allocation('Low')
        
        assert result['risk_level'] == 'Low'
        assert result['allocation']['Bonds'] == 60
        assert result['allocation']['Mutual Funds'] == 30
        assert result['allocation']['Equity'] == 10
        assert result['expected_annual_return'] == 0.08
    
    def test_suggest_portfolio_allocation_medium(self, service):
        """Test portfolio allocation for medium risk."""
        result = service.suggest_portfolio_allocation('Medium')
        
        assert result['risk_level'] == 'Medium'
        assert result['allocation']['Equity'] == 50
        assert result['allocation']['Mutual Funds'] == 30
        assert result['allocation']['Bonds'] == 20
        assert result['expected_annual_return'] == 0.12
    
    def test_suggest_portfolio_allocation_high(self, service):
        """Test portfolio allocation for high risk."""
        result = service.suggest_portfolio_allocation('High')
        
        assert result['risk_level'] == 'High'
        assert result['allocation']['Equity'] == 70
        assert result['allocation']['Mutual Funds'] == 20
        assert result['allocation']['Bonds'] == 10
        assert result['expected_annual_return'] == 0.16
    
    def test_suggest_portfolio_allocation_invalid(self, service):
        """Test portfolio allocation with invalid risk level."""
        with pytest.raises(ValueError):
            service.suggest_portfolio_allocation('Invalid')
    
    def test_get_portfolio_allocation(self, service):
        """Test simple portfolio allocation getter."""
        allocation = service.get_portfolio_allocation('Medium')
        
        assert isinstance(allocation, dict)
        assert 'Equity' in allocation
        assert 'Mutual Funds' in allocation
        assert 'Bonds' in allocation
        assert sum(allocation.values()) == 100
    
    def test_calculate_goal_plan_achievable(self, service):
        """Test complete goal plan calculation - achievable case."""
        plan = service.calculate_goal_plan(
            goal_amount=300000,
            goal_years=2,
            current_savings=50000,
            monthly_savings=20000,
            risk_level='Medium'
        )
        
        # Check structure
        assert 'goal_amount' in plan
        assert 'monthly_savings_required' in plan
        assert 'projected_amount' in plan
        assert 'portfolio_allocation' in plan
        assert 'sip_projections' in plan
        assert 'feasibility' in plan
        
        # With 20k available and likely lower requirement, should be achievable
        assert plan['feasibility'] == 'achievable'
    
    def test_calculate_goal_plan_challenging(self, service):
        """Test complete goal plan calculation - challenging case."""
        plan = service.calculate_goal_plan(
            goal_amount=1000000,
            goal_years=1,
            current_savings=0,
            monthly_savings=10000,
            risk_level='Low'
        )
        
        # Should be challenging with limited savings
        assert plan['feasibility'] == 'challenging'
        assert plan['monthly_shortfall'] > 0
        assert len(plan['recommendations']) > 0
    
    def test_calculate_goal_plan_structure(self, service):
        """Test goal plan has all required fields."""
        plan = service.calculate_goal_plan(
            goal_amount=500000,
            goal_years=3,
            current_savings=100000,
            monthly_savings=15000,
            risk_level='High'
        )
        
        required_fields = [
            'goal_amount', 'goal_years', 'current_savings',
            'monthly_savings_required', 'projected_amount',
            'expected_return_rate', 'portfolio_allocation',
            'sip_projections', 'feasibility', 'recommendations'
        ]
        
        for field in required_fields:
            assert field in plan, f"Missing field: {field}"


class TestGoalServiceCalculations:
    """Test specific calculation scenarios."""
    
    @pytest.fixture
    def service(self):
        """Fixture to create GoalService instance."""
        return GoalService()
    
    def test_long_term_goal(self, service):
        """Test long-term goal (10+ years)."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=2000000,
            goal_years=15,
            current_savings=200000,
            annual_return_rate=0.12
        )
        
        # Should be reasonable monthly amount
        assert 0 < monthly < 50000
    
    def test_short_term_goal(self, service):
        """Test short-term goal (1 year)."""
        monthly = service.calculate_monthly_savings_required(
            goal_amount=120000,
            goal_years=1,
            current_savings=0,
            annual_return_rate=0.08
        )
        
        # Roughly 10k per month (without considering returns)
        assert monthly < 11000
    
    def test_compound_interest_effect(self, service):
        """Test that compound interest reduces monthly requirement."""
        # Same goal with different rates
        monthly_low_risk = service.calculate_monthly_savings_required(
            goal_amount=500000,
            goal_years=5,
            current_savings=0,
            annual_return_rate=0.08
        )
        
        monthly_high_risk = service.calculate_monthly_savings_required(
            goal_amount=500000,
            goal_years=5,
            current_savings=0,
            annual_return_rate=0.16
        )
        
        # Higher return should require lower monthly investment
        assert monthly_high_risk < monthly_low_risk


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
