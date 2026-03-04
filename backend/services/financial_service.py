"""
Financial Service module for AI Financial Advisor.
Handles all financial calculations and risk assessments.
"""

from typing import Dict, Any
from backend.models.financial_model import FinancialMetrics


class FinancialService:
    """
    Service class for financial calculations and analysis.
    
    Provides methods for calculating:
    - Budget ratios
    - Savings rates
    - Debt-to-income ratios
    - Financial health scores
    - Risk classifications
    """
    
    def __init__(self):
        """Initialize the financial service."""
        pass
    
    def calculate_budget_ratio(self, income: float, expenses: float) -> float:
        """
        Calculate the budget ratio (expenses as percentage of income).
        
        Args:
            income: Monthly income
            expenses: Monthly expenses
            
        Returns:
            Budget ratio as a decimal (0.0 to 1.0+)
            
        Example:
            >>> service = FinancialService()
            >>> service.calculate_budget_ratio(60000, 35000)
            0.5833
        """
        if income <= 0:
            return 0.0
        return expenses / income
    
    def calculate_savings_rate(self, income: float, savings: float) -> float:
        """
        Calculate the savings rate (savings as percentage of income).
        
        Args:
            income: Monthly income
            savings: Monthly savings amount
            
        Returns:
            Savings rate as a decimal
            
        Example:
            >>> service = FinancialService()
            >>> service.calculate_savings_rate(60000, 15000)
            0.25
        """
        if income <= 0:
            return 0.0
        return savings / income
    
    def calculate_dti(self, debt: float, income: float) -> float:
        """
        Calculate the Debt-to-Income (DTI) ratio.
        
        This is a key metric used by lenders to assess creditworthiness.
        Lower DTI indicates better financial health.
        
        Args:
            debt: Monthly debt payments
            income: Monthly gross income
            
        Returns:
            DTI ratio as a decimal
            
        Example:
            >>> service = FinancialService()
            >>> service.calculate_dti(10000, 60000)
            0.1667
        """
        if income <= 0:
            return 0.0
        return debt / income
    
    def calculate_financial_health_score(
        self,
        savings_rate: float,
        dti_ratio: float,
        budget_ratio: float
    ) -> Dict[str, Any]:
        """
        Calculate overall financial health score out of 100.
        
        V2 Weighted Formula:
        - Savings Rate → 40%
        - Debt-to-Income Ratio → 30%
        - Expense Ratio → 30%
        
        Args:
            savings_rate: Savings as percentage of income
            dti_ratio: Debt-to-income ratio
            budget_ratio: Expenses as percentage of income
            
        Returns:
            Dictionary with score, breakdown, and status
        """
        # Savings rate score (40% weight) - Ideal: 20%+
        savings_score = min(savings_rate / 0.20, 1.0) * 40
        
        # DTI score (30% weight) - Ideal: <20%
        if dti_ratio <= 0.20:
            dti_score = 30
        elif dti_ratio <= 0.36:
            dti_score = 30 - ((dti_ratio - 0.20) / 0.16) * 15
        elif dti_ratio <= 0.50:
            dti_score = 15 - ((dti_ratio - 0.36) / 0.14) * 10
        else:
            dti_score = max(5 - ((dti_ratio - 0.50) / 0.50) * 5, 0)
        
        # Expense ratio score (30% weight) - Ideal: <50%
        if budget_ratio <= 0.50:
            expense_score = 30
        elif budget_ratio <= 0.70:
            expense_score = 30 - ((budget_ratio - 0.50) / 0.20) * 15
        elif budget_ratio <= 0.85:
            expense_score = 15 - ((budget_ratio - 0.70) / 0.15) * 10
        else:
            expense_score = max(5 - ((budget_ratio - 0.85) / 0.15) * 5, 0)
        
        total_score = savings_score + dti_score + expense_score
        final_score = min(max(total_score, 0), 100)
        
        return {
            'score': round(final_score, 1),
            'breakdown': {
                'savings_rate_contribution': round(savings_score, 1),
                'dti_contribution': round(dti_score, 1),
                'expense_contribution': round(expense_score, 1)
            },
            'status': self._get_health_status_label(final_score)
        }
    
    def _get_health_status_label(self, score: float) -> str:
        """Get financial status label based on score."""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Stable'
        elif score >= 40:
            return 'Fair'
        elif score >= 20:
            return 'Risky'
        else:
            return 'Critical'
    
    def classify_risk(self, dti_ratio: float) -> Dict[str, Any]:
        """
        Classify financial risk based on DTI ratio.
        
        Risk classifications:
        - Low Risk: DTI < 0.30 (30%)
        - Moderate Risk: DTI 0.30 - 0.50 (30-50%)
        - High Risk: DTI > 0.50 (50%)
        
        Args:
            dti_ratio: Debt-to-income ratio
            
        Returns:
            Dictionary with classification, description, and recommendations
        """
        if dti_ratio < 0.30:
            return {
                'classification': 'Low',
                'description': 'Your debt-to-income ratio is healthy. You have good capacity to take on additional debt if needed.',
                'recommendations': [
                    'Consider increasing investments to build wealth',
                    'Maintain your current savings rate',
                    'You may qualify for favorable loan terms'
                ]
            }
        elif dti_ratio <= 0.50:
            return {
                'classification': 'Moderate',
                'description': 'Your debt-to-income ratio is manageable but approaching cautionary levels.',
                'recommendations': [
                    'Avoid taking on new debt',
                    'Focus on debt repayment before new investments',
                    'Build an emergency fund of 3-6 months expenses'
                ]
            }
        else:
            return {
                'classification': 'High',
                'description': 'Your debt-to-income ratio is concerning. Immediate action recommended to reduce debt burden.',
                'recommendations': [
                    'Prioritize high-interest debt repayment',
                    'Consider debt consolidation options',
                    'Seek professional financial counseling',
                    'Create a strict budget and stick to it'
                ]
            }
    
    def calculate_monthly_surplus(self, income: float, expenses: float) -> float:
        """
        Calculate monthly surplus (income minus expenses).
        
        Args:
            income: Monthly income
            expenses: Monthly expenses
            
        Returns:
            Monthly surplus amount
        """
        return income - expenses
    
    def calculate_all_metrics(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        assets: Dict[str, float] = None,
        liabilities: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate all financial metrics in one call (V2 Enhanced).
        
        Args:
            income: Monthly income
            expenses: Monthly expenses
            savings: Current savings
            debt: Total debt
            assets: Dictionary of assets (optional)
            liabilities: Dictionary of liabilities (optional)
            
        Returns:
            Dictionary containing all calculated metrics
        """
        # Calculate individual metrics
        monthly_surplus = self.calculate_monthly_surplus(income, expenses)
        budget_ratio = self.calculate_budget_ratio(income, expenses)
        savings_rate = self.calculate_savings_rate(income, monthly_surplus)
        dti_ratio = self.calculate_dti(debt, income)
        
        # V2: Enhanced health score with breakdown
        health_result = self.calculate_financial_health_score(
            savings_rate, dti_ratio, budget_ratio
        )
        
        # V2: Risk classification
        risk_classification = self.classify_risk(dti_ratio)
        
        # V2: Emergency fund analysis
        emergency_fund = self.analyze_emergency_fund(savings, expenses)
        
        # V2: Net worth calculation
        if assets and liabilities:
            net_worth = self.calculate_net_worth(assets, liabilities)
        else:
            net_worth = None
        
        # Create and return metrics dictionary
        metrics = FinancialMetrics(
            income=income,
            expenses=expenses,
            savings=savings,
            debt=debt,
            monthly_surplus=monthly_surplus,
            budget_ratio=budget_ratio,
            savings_rate=savings_rate,
            debt_to_income_ratio=dti_ratio,
            financial_health_score=health_result['score']
        )
        
        result = metrics.to_dict()
        result['health_score_details'] = health_result
        result['risk_classification'] = risk_classification
        result['emergency_fund'] = emergency_fund
        
        if net_worth:
            result['net_worth'] = net_worth
        
        return result
    
    def get_financial_health_status(self, score: float) -> str:
        """
        Get textual status based on financial health score.
        
        Args:
            score: Financial health score (0-100)
            
        Returns:
            Status string (Excellent, Good, Fair, Poor, Critical)
        """
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        elif score >= 20:
            return 'Poor'
        else:
            return 'Critical'
    
    # ==================== V2 NEW FEATURES ====================
    
    def analyze_emergency_fund(
        self,
        current_savings: float,
        monthly_expenses: float
    ) -> Dict[str, Any]:
        """
        Analyze emergency fund status.
        
        Required Emergency Fund = 6 × Monthly Expenses
        
        Args:
            current_savings: Current emergency fund amount
            monthly_expenses: Monthly expenses
            
        Returns:
            Dictionary with required amount, coverage %, and status
        """
        required_amount = monthly_expenses * 6
        coverage_pct = (current_savings / required_amount * 100) if required_amount > 0 else 0
        
        if coverage_pct < 40:
            status = 'Critical'
            color = 'red'
        elif coverage_pct < 80:
            status = 'Moderate'
            color = 'yellow'
        else:
            status = 'Safe'
            color = 'green'
        
        return {
            'required_amount': round(required_amount, 2),
            'current_amount': round(current_savings, 2),
            'coverage_percentage': round(coverage_pct, 1),
            'status': status,
            'color': color,
            'deficit': round(max(0, required_amount - current_savings), 2)
        }
    
    def calculate_net_worth(
        self,
        assets: Dict[str, float],
        liabilities: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate net worth.
        
        Net Worth = Total Assets − Total Liabilities
        
        Args:
            assets: Dictionary of asset categories and values
            liabilities: Dictionary of liability categories and values
            
        Returns:
            Dictionary with net worth breakdown
        """
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        net_worth = total_assets - total_liabilities
        
        return {
            'total_assets': round(total_assets, 2),
            'total_liabilities': round(total_liabilities, 2),
            'net_worth': round(net_worth, 2),
            'status': 'Positive' if net_worth >= 0 else 'Negative',
            'asset_breakdown': assets,
            'liability_breakdown': liabilities
        }
    
    def calculate_compound_projection(
        self,
        principal: float,
        monthly_contribution: float,
        years: int,
        annual_rate: float,
        compounds_per_year: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate compound growth projection.
        
        Formula: A = P(1 + r/n)^(nt) + PMT × [((1 + r/n)^(nt) - 1) / (r/n)]
        
        Args:
            principal: Initial investment amount
            monthly_contribution: Monthly contribution
            years: Investment period in years
            annual_rate: Annual interest rate (decimal)
            compounds_per_year: Number of times interest compounds per year
            
        Returns:
            Dictionary with projection data
        """
        n = compounds_per_year
        t = years
        r = annual_rate
        PMT = monthly_contribution
        
        # Compound interest formula with contributions
        amount = principal * (1 + r/n)**(n*t)
        if r > 0:
            amount += PMT * (((1 + r/n)**(n*t) - 1) / (r/n))
        else:
            amount += PMT * n * t
        
        total_contributions = principal + (monthly_contribution * 12 * years)
        interest_earned = amount - total_contributions
        
        return {
            'final_amount': round(amount, 2),
            'total_contributions': round(total_contributions, 2),
            'interest_earned': round(interest_earned, 2),
            'growth_percentage': round((interest_earned / total_contributions) * 100, 1) if total_contributions > 0 else 0
        }
    
    def get_goal_projections(
        self,
        principal: float,
        monthly_contribution: float,
        years: int
    ) -> Dict[str, Any]:
        """
        Get compound projections for different scenarios.
        
        Scenarios:
        - Conservative: 8%
        - Moderate: 12%
        - Aggressive: 15%
        
        Args:
            principal: Initial investment
            monthly_contribution: Monthly contribution
            years: Investment period
            
        Returns:
            Dictionary with all scenario projections
        """
        scenarios = {
            'conservative': 0.08,
            'moderate': 0.12,
            'aggressive': 0.15
        }
        
        projections = {}
        for name, rate in scenarios.items():
            projections[name] = self.calculate_compound_projection(
                principal, monthly_contribution, years, rate
            )
        
        return projections
    
    def simulate_what_if(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        income_change_pct: float = 0,
        expense_change_pct: float = 0,
        return_rate_pct: float = 0
    ) -> Dict[str, Any]:
        """
        Run what-if simulation.
        
        Args:
            income: Current monthly income
            expenses: Current monthly expenses
            savings: Current savings
            debt: Current debt
            income_change_pct: Income change percentage
            expense_change_pct: Expense change percentage
            return_rate_pct: Investment return rate percentage
            
        Returns:
            Dictionary with impact analysis
        """
        # Apply changes
        new_income = income * (1 + income_change_pct / 100)
        new_expenses = expenses * (1 + expense_change_pct / 100)
        new_surplus = new_income - new_expenses
        
        # Calculate new metrics
        new_budget_ratio = new_expenses / new_income if new_income > 0 else 0
        new_savings_rate = new_surplus / new_income if new_income > 0 else 0
        new_dti = debt / (new_income * 12) if new_income > 0 else 0
        
        health_result = self.calculate_financial_health_score(
            new_savings_rate, new_dti, new_budget_ratio
        )
        
        # Calculate goal timeline impact (simplified)
        current_monthly_savings = income - expenses
        new_monthly_savings = new_income - new_expenses
        
        timeline_impact = {}
        if current_monthly_savings > 0 and new_monthly_savings > 0:
            timeline_change = ((current_monthly_savings / new_monthly_savings) - 1) * 100
            timeline_impact = {
                'timeline_change_pct': round(timeline_change, 1),
                'faster_payoff': timeline_change < 0
            }
        
        return {
            'new_income': round(new_income, 2),
            'new_expenses': round(new_expenses, 2),
            'new_monthly_surplus': round(new_surplus, 2),
            'new_savings_rate': round(new_savings_rate * 100, 1),
            'new_dti': round(new_dti * 100, 1),
            'health_score': health_result,
            'timeline_impact': timeline_impact
        }
