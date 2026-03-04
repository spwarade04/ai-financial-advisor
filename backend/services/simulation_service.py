"""
Risk Simulation Engine Service.
Simulates various financial scenarios and their impacts.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from backend.models.financial_record_model import FinancialRecord


@dataclass
class SimulationScenario:
    """Simulation scenario definition."""
    name: str
    description: str
    income_change: float  # Percentage change
    expense_change: float  # Percentage change
    interest_rate_change: float  # Percentage point change


@dataclass
class SimulationResult:
    """Simulation result."""
    scenario: SimulationScenario
    original_savings_rate: float
    simulated_savings_rate: float
    original_dti: float
    simulated_dti: float
    impact_on_timeline: str
    risk_level: str
    recommendations: List[str]


class SimulationService:
    """
    Service for running financial risk simulations.
    """
    
    # Predefined scenarios
    SCENARIOS = {
        'income_drop_20': SimulationScenario(
            name='Income Drop (-20%)',
            description='Simulates a 20% reduction in monthly income (job loss, pay cut)',
            income_change=-20.0,
            expense_change=0.0,
            interest_rate_change=0.0
        ),
        'income_drop_50': SimulationScenario(
            name='Income Drop (-50%)',
            description='Simulates a 50% reduction in monthly income (severe job loss)',
            income_change=-50.0,
            expense_change=0.0,
            interest_rate_change=0.0
        ),
        'expense_spike_30': SimulationScenario(
            name='Expense Spike (+30%)',
            description='Simulates a 30% increase in monthly expenses (medical emergency, repairs)',
            income_change=0.0,
            expense_change=30.0,
            interest_rate_change=0.0
        ),
        'expense_spike_50': SimulationScenario(
            name='Expense Spike (+50%)',
            description='Simulates a 50% increase in monthly expenses (major emergency)',
            income_change=0.0,
            expense_change=50.0,
            interest_rate_change=0.0
        ),
        'interest_rate_rise_3': SimulationScenario(
            name='Interest Rate Rise (+3%)',
            description='Simulates a 3 percentage point increase in interest rates',
            income_change=0.0,
            expense_change=5.0,  # Estimated impact on debt payments
            interest_rate_change=3.0
        ),
        'combined_stress': SimulationScenario(
            name='Combined Stress Test',
            description='Simulates income drop (-15%) with expense spike (+20%)',
            income_change=-15.0,
            expense_change=20.0,
            interest_rate_change=1.0
        )
    }
    
    @classmethod
    def run_simulation(
        cls,
        financial_record: FinancialRecord,
        scenario_key: str
    ) -> SimulationResult:
        """
        Run a predefined simulation scenario.
        
        Args:
            financial_record: User's financial record
            scenario_key: Key of the scenario to run
            
        Returns:
            SimulationResult with impact analysis
        """
        if scenario_key not in cls.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_key}")
        
        scenario = cls.SCENARIOS[scenario_key]
        return cls._calculate_impact(financial_record, scenario)
    
    @classmethod
    def run_custom_simulation(
        cls,
        financial_record: FinancialRecord,
        name: str,
        income_change: float,
        expense_change: float,
        interest_rate_change: float = 0.0,
        description: str = ""
    ) -> SimulationResult:
        """
        Run a custom simulation scenario.
        
        Args:
            financial_record: User's financial record
            name: Scenario name
            income_change: Income change percentage
            expense_change: Expense change percentage
            interest_rate_change: Interest rate change in percentage points
            description: Scenario description
            
        Returns:
            SimulationResult with impact analysis
        """
        scenario = SimulationScenario(
            name=name,
            description=description or f"Custom scenario: Income {income_change:+.1f}%, Expenses {expense_change:+.1f}%",
            income_change=income_change,
            expense_change=expense_change,
            interest_rate_change=interest_rate_change
        )
        
        return cls._calculate_impact(financial_record, scenario)
    
    @classmethod
    def _calculate_impact(
        cls,
        record: FinancialRecord,
        scenario: SimulationScenario
    ) -> SimulationResult:
        """
        Calculate the impact of a scenario.
        
        Args:
            record: Financial record
            scenario: Simulation scenario
            
        Returns:
            SimulationResult
        """
        # Original values
        original_income = record.monthly_income
        original_expenses = record.monthly_expenses
        original_savings_rate = record.savings_rate
        original_dti = record.dti_ratio
        
        # Calculate simulated values
        simulated_income = original_income * (1 + scenario.income_change / 100)
        simulated_expenses = original_expenses * (1 + scenario.expense_change / 100)
        
        # Add interest rate impact to expenses (estimated)
        if scenario.interest_rate_change > 0:
            interest_impact = record.total_liabilities * (scenario.interest_rate_change / 100) / 12
            simulated_expenses += interest_impact
        
        # Calculate simulated metrics
        simulated_savings = simulated_income - simulated_expenses
        simulated_savings_rate = (simulated_savings / simulated_income * 100) if simulated_income > 0 else 0
        
        # Calculate simulated DTI
        monthly_debt_payment = record.total_liabilities * 0.05  # Assume 5% monthly
        if scenario.interest_rate_change > 0:
            monthly_debt_payment *= (1 + scenario.interest_rate_change / 100)
        simulated_dti = (monthly_debt_payment / simulated_income * 100) if simulated_income > 0 else 100
        
        # Determine risk level
        risk_level = cls._determine_risk_level(
            simulated_savings_rate, simulated_dti, simulated_income, simulated_expenses
        )
        
        # Calculate timeline impact
        timeline_impact = cls._calculate_timeline_impact(
            record, original_savings_rate, simulated_savings_rate
        )
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(
            scenario, simulated_savings_rate, simulated_dti, risk_level
        )
        
        return SimulationResult(
            scenario=scenario,
            original_savings_rate=round(original_savings_rate, 2),
            simulated_savings_rate=round(simulated_savings_rate, 2),
            original_dti=round(original_dti, 2),
            simulated_dti=round(simulated_dti, 2),
            impact_on_timeline=timeline_impact,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    @classmethod
    def _determine_risk_level(
        cls,
        savings_rate: float,
        dti: float,
        income: float,
        expenses: float
    ) -> str:
        """
        Determine risk level based on simulated metrics.
        
        Args:
            savings_rate: Simulated savings rate
            dti: Simulated debt-to-income ratio
            income: Simulated income
            expenses: Simulated expenses
            
        Returns:
            Risk level string
        """
        # Critical conditions
        if income < expenses or savings_rate < -10 or dti > 60:
            return 'Critical'
        
        # High risk conditions
        if savings_rate < 0 or dti > 40 or (income - expenses) < 0.1 * income:
            return 'High'
        
        # Medium risk conditions
        if savings_rate < 10 or dti > 30:
            return 'Medium'
        
        return 'Low'
    
    @classmethod
    def _calculate_timeline_impact(
        cls,
        record: FinancialRecord,
        original_savings_rate: float,
        simulated_savings_rate: float
    ) -> str:
        """
        Calculate impact on financial goals timeline.
        
        Args:
            record: Financial record
            original_savings_rate: Original savings rate
            simulated_savings_rate: Simulated savings rate
            
        Returns:
            Timeline impact description
        """
        if simulated_savings_rate <= 0:
            return "Goals cannot be met under this scenario. Immediate action required."
        
        if original_savings_rate <= 0:
            return "Unable to calculate impact due to negative original savings rate."
        
        # Calculate delay factor
        delay_factor = original_savings_rate / simulated_savings_rate
        
        if delay_factor > 2:
            return f"Goals will take {delay_factor:.1f}x longer to achieve. Major adjustments needed."
        elif delay_factor > 1.5:
            return f"Goals will take {delay_factor:.1f}x longer. Consider reducing goal amounts."
        elif delay_factor > 1.2:
            return f"Goals will take {delay_factor:.1f}x longer. Manageable with minor adjustments."
        else:
            return "Minimal impact on goal timelines. Current plan remains viable."
    
    @classmethod
    def _generate_recommendations(
        cls,
        scenario: SimulationScenario,
        savings_rate: float,
        dti: float,
        risk_level: str
    ) -> List[str]:
        """
        Generate recommendations based on simulation results.
        
        Args:
            scenario: The simulation scenario
            savings_rate: Simulated savings rate
            dti: Simulated DTI
            risk_level: Risk level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_level == 'Critical':
            recommendations.extend([
                "URGENT: Build larger emergency fund immediately (target 9-12 months)",
                "Consider debt consolidation or refinancing options",
                "Explore additional income sources or side hustles",
                "Review and cut all non-essential expenses"
            ])
        elif risk_level == 'High':
            recommendations.extend([
                "Increase emergency fund to 6-8 months of expenses",
                "Delay non-essential large purchases",
                "Consider income protection insurance",
                "Create a bare-bones budget for crisis scenarios"
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                "Maintain 6-month emergency fund",
                "Monitor expenses closely during transition periods",
                "Build flexibility into your financial plan"
            ])
        else:
            recommendations.append("Your finances are resilient to this scenario. Continue current strategy.")
        
        # Scenario-specific recommendations
        if scenario.income_change < -30:
            recommendations.append("Severe income drop: Consider career transition planning and skill development.")
        
        if scenario.expense_change > 30:
            recommendations.append("Major expense spike: Review insurance coverage for emergencies.")
        
        if scenario.interest_rate_change > 2:
            recommendations.append("Rising rates: Consider fixing interest rates on variable loans.")
        
        return recommendations
    
    @classmethod
    def get_available_scenarios(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get list of available simulation scenarios.
        
        Returns:
            Dictionary of scenario descriptions
        """
        return {
            key: {
                'name': scenario.name,
                'description': scenario.description,
                'income_change': scenario.income_change,
                'expense_change': scenario.expense_change,
                'interest_rate_change': scenario.interest_rate_change
            }
            for key, scenario in cls.SCENARIOS.items()
        }
    
    @classmethod
    def to_dict(cls, result: SimulationResult) -> Dict[str, Any]:
        """
        Convert simulation result to dictionary.
        
        Args:
            result: SimulationResult object
            
        Returns:
            Dictionary representation
        """
        return {
            'scenario': {
                'name': result.scenario.name,
                'description': result.scenario.description,
                'income_change': result.scenario.income_change,
                'expense_change': result.scenario.expense_change,
                'interest_rate_change': result.scenario.interest_rate_change
            },
            'metrics': {
                'original_savings_rate': result.original_savings_rate,
                'simulated_savings_rate': result.simulated_savings_rate,
                'original_dti': result.original_dti,
                'simulated_dti': result.simulated_dti
            },
            'impact_on_timeline': result.impact_on_timeline,
            'risk_level': result.risk_level,
            'recommendations': result.recommendations
        }
