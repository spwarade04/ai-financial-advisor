"""
Unit tests for Financial Service.
Tests all financial calculation methods.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.financial_service import FinancialService


class TestFinancialService:
    """Test class for FinancialService."""
    
    @pytest.fixture
    def service(self):
        """Fixture to create FinancialService instance."""
        return FinancialService()
    
    def test_calculate_budget_ratio(self, service):
        """Test budget ratio calculation."""
        # Normal case
        assert service.calculate_budget_ratio(60000, 35000) == pytest.approx(0.5833, abs=0.001)
        
        # Edge case: zero income
        assert service.calculate_budget_ratio(0, 35000) == 0.0
        
        # Edge case: zero expenses
        assert service.calculate_budget_ratio(60000, 0) == 0.0
        
        # Case: expenses equal income
        assert service.calculate_budget_ratio(60000, 60000) == 1.0
    
    def test_calculate_savings_rate(self, service):
        """Test savings rate calculation."""
        # Normal case
        assert service.calculate_savings_rate(60000, 15000) == pytest.approx(0.25, abs=0.001)
        
        # Edge case: zero income
        assert service.calculate_savings_rate(0, 15000) == 0.0
        
        # Edge case: zero savings
        assert service.calculate_savings_rate(60000, 0) == 0.0
        
        # Case: savings equal income
        assert service.calculate_savings_rate(60000, 60000) == 1.0
    
    def test_calculate_dti(self, service):
        """Test debt-to-income ratio calculation."""
        # Normal case
        assert service.calculate_dti(10000, 60000) == pytest.approx(0.1667, abs=0.001)
        
        # Edge case: zero income
        assert service.calculate_dti(10000, 0) == 0.0
        
        # Edge case: zero debt
        assert service.calculate_dti(0, 60000) == 0.0
        
        # Case: debt equals income
        assert service.calculate_dti(60000, 60000) == 1.0
    
    def test_calculate_financial_health_score(self, service):
        """Test financial health score calculation."""
        # Excellent score case
        score = service.calculate_financial_health_score(0.25, 0.10, 0.50)
        assert score > 80
        
        # Poor score case
        score = service.calculate_financial_health_score(0.05, 0.60, 0.90)
        assert score < 40
        
        # Score should be between 0 and 100
        score = service.calculate_financial_health_score(0.15, 0.30, 0.70)
        assert 0 <= score <= 100
    
    def test_classify_risk_low(self, service):
        """Test risk classification for low DTI."""
        result = service.classify_risk(0.20)
        assert result['classification'] == 'Low'
        assert 'healthy' in result['description'].lower()
        assert len(result['recommendations']) > 0
    
    def test_classify_risk_moderate(self, service):
        """Test risk classification for moderate DTI."""
        result = service.classify_risk(0.40)
        assert result['classification'] == 'Moderate'
        assert 'manageable' in result['description'].lower()
    
    def test_classify_risk_high(self, service):
        """Test risk classification for high DTI."""
        result = service.classify_risk(0.60)
        assert result['classification'] == 'High'
        assert 'concerning' in result['description'].lower()
    
    def test_calculate_monthly_surplus(self, service):
        """Test monthly surplus calculation."""
        assert service.calculate_monthly_surplus(60000, 35000) == 25000
        assert service.calculate_monthly_surplus(60000, 60000) == 0
        assert service.calculate_monthly_surplus(35000, 60000) == -25000
    
    def test_calculate_all_metrics(self, service):
        """Test comprehensive metrics calculation."""
        metrics = service.calculate_all_metrics(
            income=60000,
            expenses=35000,
            savings=100000,
            debt=50000
        )
        
        # Check all expected keys
        expected_keys = [
            'income', 'expenses', 'savings', 'debt',
            'monthly_surplus', 'budget_ratio', 'savings_rate',
            'debt_to_income_ratio', 'financial_health_score'
        ]
        for key in expected_keys:
            assert key in metrics
        
        # Verify calculations
        assert metrics['monthly_surplus'] == 25000
        assert metrics['budget_ratio'] == pytest.approx(0.5833, abs=0.001)
        assert metrics['debt_to_income_ratio'] == pytest.approx(0.8333, abs=0.001)
    
    def test_get_financial_health_status(self, service):
        """Test health status text generation."""
        assert service.get_financial_health_status(85) == 'Excellent'
        assert service.get_financial_health_status(70) == 'Good'
        assert service.get_financial_health_status(50) == 'Fair'
        assert service.get_financial_health_status(30) == 'Poor'
        assert service.get_financial_health_status(10) == 'Critical'


class TestFinancialServiceEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def service(self):
        """Fixture to create FinancialService instance."""
        return FinancialService()
    
    def test_negative_values(self, service):
        """Test handling of negative values."""
        # These should still calculate but may not make financial sense
        assert service.calculate_budget_ratio(-60000, 35000) == pytest.approx(-0.5833, abs=0.001)
        assert service.calculate_dti(-10000, 60000) == pytest.approx(-0.1667, abs=0.001)
    
    def test_very_large_numbers(self, service):
        """Test handling of very large numbers."""
        large_income = 1000000000  # 1 billion
        large_expense = 500000000  # 500 million
        
        ratio = service.calculate_budget_ratio(large_income, large_expense)
        assert ratio == 0.5
    
    def test_very_small_numbers(self, service):
        """Test handling of very small numbers."""
        small_income = 0.01
        small_expense = 0.005
        
        ratio = service.calculate_budget_ratio(small_income, small_expense)
        assert ratio == 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
