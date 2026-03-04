"""
AI Service module for AI Financial Advisor.
Integrates with Google Gemini for intelligent financial recommendations.
"""

import json
import os
import hashlib
import time
from typing import Dict, Any, Optional
from functools import lru_cache
from google import genai
from google.genai import types
from config import get_config


# Simple in-memory cache for AI responses
_ai_cache = {}
_cache_ttl = 3600  # 1 hour


def _get_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def _get_cached_response(cache_key: str) -> Optional[str]:
    """Get cached response if valid."""
    if cache_key in _ai_cache:
        timestamp, response = _ai_cache[cache_key]
        if time.time() - timestamp < _cache_ttl:
            return response
        else:
            del _ai_cache[cache_key]
    return None


def _cache_response(cache_key: str, response: str):
    """Cache AI response."""
    _ai_cache[cache_key] = (time.time(), response)


class AIService:
    """
    Service class for AI-powered financial recommendations.
    
    Uses Google's Gemini Flash model to generate:
    - Personalized financial advice
    - Budget optimization strategies
    - Debt management plans
    - Investment recommendations
    - Long-term financial roadmaps
    """
    
    def __init__(self):
        """Initialize the AI service with Gemini configuration."""
        config = get_config()
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.GEMINI_MODEL
        self.model = None
        
        if self.api_key:
            self._configure_gemini()
    
    def _configure_gemini(self) -> None:
        """Configure Gemini API with API key."""
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Warning: Failed to configure Gemini API: {e}")
            self.client = None
    
    def _build_prompt(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        goal_amount: float,
        goal_years: int,
        risk_level: str,
        financial_metrics: Dict[str, Any],
        goal_plan: Dict[str, Any],
        risk_classification: Dict[str, Any]
    ) -> str:
        """
        Build a comprehensive prompt for Gemini.
        
        Args:
            income: Monthly income
            expenses: Monthly expenses
            savings: Current savings
            debt: Total debt
            goal_amount: Financial goal target
            goal_years: Time horizon
            risk_level: Risk appetite
            financial_metrics: Calculated financial metrics
            goal_plan: Goal-based plan details
            risk_classification: Risk classification details
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert AI Financial Advisor. Analyze the following financial profile and provide comprehensive, actionable advice.

## USER FINANCIAL PROFILE

### Income & Expenses
- Monthly Income: ₹{income:,.2f}
- Monthly Expenses: ₹{expenses:,.2f}
- Current Savings: ₹{savings:,.2f}
- Total Debt: ₹{debt:,.2f}

### Financial Goals
- Target Amount: ₹{goal_amount:,.2f}
- Time Horizon: {goal_years} years
- Risk Appetite: {risk_level}

### Financial Health Metrics
- Monthly Surplus: ₹{financial_metrics.get('monthly_surplus', 0):,.2f}
- Budget Ratio: {financial_metrics.get('budget_ratio', 0)*100:.1f}%
- Savings Rate: {financial_metrics.get('savings_rate', 0)*100:.1f}%
- Debt-to-Income Ratio: {financial_metrics.get('debt_to_income_ratio', 0)*100:.1f}%
- Financial Health Score: {financial_metrics.get('financial_health_score', 0):.0f}/100

### Risk Assessment
- Classification: {risk_classification.get('classification', 'Unknown')}
- Description: {risk_classification.get('description', '')}

### Goal Plan
- Monthly Savings Required: ₹{goal_plan.get('monthly_savings_required', 0):,.2f}
- Projected Amount: ₹{goal_plan.get('projected_amount', 0):,.2f}
- Expected Return: {goal_plan.get('expected_return_rate', 0)*100:.1f}%
- Portfolio Allocation: {json.dumps(goal_plan.get('portfolio_allocation', {}))}
- Feasibility: {goal_plan.get('feasibility', 'unknown')}

## REQUIRED OUTPUT FORMAT

Provide your response in the following structured format:

### 1. EXECUTIVE SUMMARY
A 2-3 sentence overview of the user's financial situation and main recommendation.

### 2. BUDGET OPTIMIZATION
- Identify areas for expense reduction
- Suggest realistic savings targets
- Recommend budget allocation (50/30/20 rule analysis)

### 3. DEBT MANAGEMENT STRATEGY
- Prioritize debt repayment approach
- Suggest consolidation options if applicable
- Timeline for becoming debt-free

### 4. INVESTMENT RECOMMENDATIONS
- Explain the suggested portfolio allocation
- Specific investment vehicles (mutual funds, ETFs, bonds)
- SIP strategy and expected outcomes

### 5. LONG-TERM FINANCIAL ROADMAP
- 1-year milestones
- 3-year milestones  
- 5-year+ vision
- Key actions to take each quarter

### 6. ACTION ITEMS (Priority Order)
List 5-7 specific, actionable steps the user should take immediately.

## TONE AND STYLE
- Be encouraging but realistic
- Use Indian financial context (INR, SIP, mutual funds)
- Provide specific numbers and percentages
- Keep advice practical and implementable
- Address both short-term wins and long-term strategy

Generate your comprehensive financial advice now:"""
        
        return prompt
    
    def generate_financial_advice(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        goal_amount: float,
        goal_years: int,
        risk_level: str,
        financial_metrics: Dict[str, Any],
        goal_plan: Dict[str, Any],
        risk_classification: Dict[str, Any]
    ) -> str:
        """
        Generate AI-powered financial advice using Gemini (V2 with caching).
        
        Args:
            income: Monthly income
            expenses: Monthly expenses
            savings: Current savings
            debt: Total debt
            goal_amount: Financial goal target
            goal_years: Time horizon
            risk_level: Risk appetite
            financial_metrics: Calculated financial metrics
            goal_plan: Goal-based plan details
            risk_classification: Risk classification details
            
        Returns:
            AI-generated financial advice string
        """
        # Check cache first
        cache_key = _get_cache_key(
            'financial_advice', income, expenses, savings, debt,
            goal_amount, goal_years, risk_level
        )
        cached_response = _get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Check if Gemini is configured
        if not self.api_key or not self.client:
            return self._generate_fallback_advice(
                income, expenses, savings, debt, goal_amount,
                goal_years, risk_level, financial_metrics,
                goal_plan, risk_classification
            )
        
        try:
            # Build the prompt
            prompt = self._build_prompt(
                income, expenses, savings, debt, goal_amount,
                goal_years, risk_level, financial_metrics,
                goal_plan, risk_classification
            )
            
            # Generate response from Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                    top_p=0.9,
                    top_k=40
                )
            )
            
            if response and response.text:
                # Cache the response
                _cache_response(cache_key, response.text)
                return response.text
            else:
                return self._generate_fallback_advice(
                    income, expenses, savings, debt, goal_amount,
                    goal_years, risk_level, financial_metrics,
                    goal_plan, risk_classification
                )
                
        except Exception as e:
            print(f"Error generating AI advice: {e}")
            return self._generate_fallback_advice(
                income, expenses, savings, debt, goal_amount,
                goal_years, risk_level, financial_metrics,
                goal_plan, risk_classification
            )
    
    def _generate_fallback_advice(
        self,
        income: float,
        expenses: float,
        savings: float,
        debt: float,
        goal_amount: float,
        goal_years: int,
        risk_level: str,
        financial_metrics: Dict[str, Any],
        goal_plan: Dict[str, Any],
        risk_classification: Dict[str, Any]
    ) -> str:
        """
        Generate fallback advice when Gemini API is unavailable.
        
        Args:
            All same parameters as generate_financial_advice
            
        Returns:
            Template-based financial advice
        """
        monthly_surplus = financial_metrics.get('monthly_surplus', 0)
        savings_rate = financial_metrics.get('savings_rate', 0) * 100
        dti = financial_metrics.get('debt_to_income_ratio', 0) * 100
        health_score = financial_metrics.get('financial_health_score', 0)
        monthly_required = goal_plan.get('monthly_savings_required', 0)
        feasibility = goal_plan.get('feasibility', 'unknown')
        
        advice = f"""## EXECUTIVE SUMMARY

Based on your financial profile with a monthly income of ₹{income:,.0f} and health score of {health_score:.0f}/100, here's your personalized financial roadmap.

---

## 1. BUDGET OPTIMIZATION

**Current Status:**
- Your expense ratio is {(expenses/income)*100:.1f}% of income
- Current savings rate: {savings_rate:.1f}%
- Monthly surplus: ₹{monthly_surplus:,.0f}

**Recommendations:**
- **Target Savings Rate:** Aim for 20% minimum, ideally 30%
- **50/30/20 Rule:** Try to allocate 50% needs, 30% wants, 20% savings
- **Expense Audit:** Review discretionary spending to increase surplus

---

## 2. DEBT MANAGEMENT STRATEGY

**Current DTI Ratio:** {dti:.1f}%
**Risk Level:** {risk_classification.get('classification', 'Unknown')}

**Action Plan:**
"""
        
        if dti > 40:
            advice += """
- **Priority 1:** Aggressive debt repayment before investing
- Consider debt consolidation for lower interest rates
- Allocate 70% of surplus to debt, 30% to emergency fund
"""
        elif dti > 20:
            advice += """
- **Balanced Approach:** Split surplus 50/50 between debt and investments
- Focus on high-interest debts first (avalanche method)
- Maintain minimum payments on all debts
"""
        else:
            advice += """
- **Low Debt Burden:** Your DTI is healthy
- Continue minimum payments, focus on wealth building
- Consider leveraging good credit for wealth-building opportunities
"""
        
        advice += f"""
---

## 3. INVESTMENT RECOMMENDATIONS

**Goal:** ₹{goal_amount:,.0f} in {goal_years} years
**Risk Profile:** {risk_level}
**Monthly Investment Needed:** ₹{monthly_required:,.0f}

**Portfolio Strategy ({risk_level} Risk):**
"""
        
        allocation = goal_plan.get('portfolio_allocation', {})
        for asset, percentage in allocation.items():
            advice += f"- {asset}: {percentage}%\n"
        
        advice += f"""
**SIP Strategy:**
- Start monthly SIP of ₹{monthly_required:,.0f} immediately
- Expected returns: {goal_plan.get('expected_return_rate', 0)*100:.1f}% annually
- Projected corpus: ₹{goal_plan.get('projected_amount', 0):,.0f}

---

## 4. LONG-TERM FINANCIAL ROADMAP

**Year 1:**
- Build emergency fund (3 months expenses = ₹{expenses*3:,.0f})
- Start SIP with ₹{monthly_required:,.0f} monthly
- Reduce discretionary expenses by 10%

**Year 2-3:**
- Increase SIP by 10% annually (step-up SIP)
- Review and rebalance portfolio
- Target: 50% of goal amount accumulated

**Year 5+:**
- Achieve financial goal
- Continue investments for next goal
- Consider diversification into real estate/equity

---

## 5. IMMEDIATE ACTION ITEMS

1. **Set up auto-debit** for ₹{monthly_required:,.0f} monthly SIP
2. **Create emergency fund** with ₹{expenses:,.0f} (1 month expense) this month
3. **Review subscriptions** and cancel unused services
4. **Track expenses** daily for next 30 days
5. **Open separate savings account** for goal-specific savings
6. **Schedule quarterly reviews** of financial progress
7. **Increase income:** Explore side hustles or skill upgrades

---

*Note: This is template-based advice. For AI-powered personalized recommendations, please configure your Gemini API key in the .env file.*
"""
        
        return advice
    
    def analyze_finances(self, record_data: Dict[str, Any]) -> str:
        """
        Analyze financial data and generate recommendations.
        
        Args:
            record_data: Financial record data dictionary
            
        Returns:
            AI-generated financial analysis string
        """
        # Extract data from record
        income = record_data.get('monthly_income', 0)
        expenses = record_data.get('monthly_expenses', 0)
        savings = record_data.get('cash_savings', 0)
        debt = record_data.get('total_liabilities', 0)
        
        # Calculate metrics
        monthly_surplus = income - expenses
        savings_rate = monthly_surplus / income if income > 0 else 0
        dti = debt / (income * 12) if income > 0 else 0
        
        financial_metrics = {
            'monthly_surplus': monthly_surplus,
            'budget_ratio': expenses / income if income > 0 else 0,
            'savings_rate': savings_rate,
            'debt_to_income_ratio': dti,
            'financial_health_score': min(100, (savings_rate * 100) + (1 - dti) * 50)
        }
        
        goal_plan = {
            'monthly_savings_required': monthly_surplus * 0.5,
            'projected_amount': savings + (monthly_surplus * 0.5 * 12 * 5),
            'expected_return_rate': 0.10,
            'portfolio_allocation': {
                'Equity Mutual Funds': 60,
                'Debt Funds': 30,
                'Gold/Commodities': 10
            },
            'feasibility': 'achievable' if monthly_surplus > 0 else 'challenging'
        }
        
        risk_classification = {
            'classification': 'Low Risk' if dti < 0.2 else 'Medium Risk' if dti < 0.4 else 'High Risk',
            'description': 'Manageable debt levels' if dti < 0.4 else 'High debt burden requires attention'
        }
        
        # Generate advice using existing method
        return self.generate_financial_advice(
            income=income,
            expenses=expenses,
            savings=savings,
            debt=debt,
            goal_amount=savings * 2,  # Default goal: double current savings
            goal_years=5,
            risk_level='moderate',
            financial_metrics=financial_metrics,
            goal_plan=goal_plan,
            risk_classification=risk_classification
        )
    
    def is_configured(self) -> bool:
        """Check if the AI service is properly configured."""
        return self.api_key is not None and self.model is not None
