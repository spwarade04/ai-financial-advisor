"""
AI Financial Chat Service.
Provides conversational AI assistance with financial context.
"""

import os
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from google import genai
from google.genai import types
from backend.models.financial_record_model import FinancialRecord
from backend.models.goal_model import Goal
from backend.utils.logger import log_ai_api_call, log_error
from config import Config


@dataclass
class ChatMessage:
    """Single chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatContext:
    """Chat context with conversation history."""
    user_id: int
    messages: List[ChatMessage] = field(default_factory=list)
    max_history: int = 10
    
    def add_message(self, role: str, content: str):
        """Add message to history."""
        self.messages.append(ChatMessage(role=role, content=content))
        # Trim history if exceeds max
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_history_text(self) -> str:
        """Get conversation history as text."""
        return "\n".join([
            f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
            for msg in self.messages[-self.max_history:]
        ])


class ChatService:
    """
    Service for AI-powered financial chat.
    """
    
    # System prompt for financial advisor persona
    SYSTEM_PROMPT = """You are an expert AI Financial Advisor. Your role is to provide personalized, 
practical financial advice based on the user's financial data and goals.

Guidelines:
1. Be concise but thorough - provide actionable advice
2. Use Indian Rupee (₹) formatting for all monetary values
3. Reference the user's specific financial data when relevant
4. Consider the user's goals, income, expenses, assets, and liabilities
5. Provide context-aware recommendations
6. Be supportive but realistic about financial challenges
7. Always prioritize emergency fund and debt management
8. Format responses with clear sections when appropriate

Current Date: {current_date}
"""
    
    # In-memory chat contexts (in production, use Redis or database)
    _chat_contexts: Dict[int, ChatContext] = {}
    
    def __init__(self):
        """Initialize chat service with Gemini API."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = Config.GEMINI_MODEL
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
    
    def chat(
        self,
        user_id: int,
        question: str,
        financial_record: Optional[FinancialRecord] = None,
        goals: Optional[List[Goal]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return AI response.
        
        Args:
            user_id: User ID
            question: User's question
            financial_record: User's financial data (optional)
            goals: User's goals (optional)
            
        Returns:
            Response dictionary with answer and metadata
        """
        if not self.client:
            return {
                'success': False,
                'error': 'AI service not configured',
                'message': 'Please set GEMINI_API_KEY environment variable'
            }
        
        try:
            # Get or create chat context
            context = self._get_context(user_id)
            
            # Build prompt with context
            prompt = self._build_prompt(question, context, financial_record, goals)
            
            # Call AI API
            start_time = time.time()
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            duration_ms = (time.time() - start_time) * 1000
            
            # Log API call
            log_ai_api_call(Config.GEMINI_MODEL, len(prompt), True, duration_ms)
            
            # Extract response text
            answer = response.text if response else "I apologize, but I couldn't generate a response. Please try again."
            
            # Update context
            context.add_message('user', question)
            context.add_message('assistant', answer)
            
            return {
                'success': True,
                'question': question,
                'answer': answer,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error(e, {'service': 'chat', 'user_id': user_id})
            log_ai_api_call(Config.GEMINI_MODEL, len(question), False, 0)
            return {
                'success': False,
                'error': 'AI service error',
                'message': str(e)
            }
    
    def _get_context(self, user_id: int) -> ChatContext:
        """Get or create chat context for user."""
        if user_id not in self._chat_contexts:
            self._chat_contexts[user_id] = ChatContext(user_id=user_id)
        return self._chat_contexts[user_id]
    
    def _build_prompt(
        self,
        question: str,
        context: ChatContext,
        financial_record: Optional[FinancialRecord],
        goals: Optional[List[Goal]]
    ) -> str:
        """
        Build comprehensive prompt with context.
        
        Args:
            question: User question
            context: Chat context
            financial_record: Financial data
            goals: User goals
            
        Returns:
            Complete prompt string
        """
        parts = []
        
        # System prompt
        parts.append(self.SYSTEM_PROMPT.format(current_date=datetime.utcnow().strftime('%Y-%m-%d')))
        
        # Financial context
        if financial_record:
            parts.append("\n--- USER'S FINANCIAL PROFILE ---")
            parts.append(self._format_financial_data(financial_record))
        
        # Goals context
        if goals:
            parts.append("\n--- USER'S FINANCIAL GOALS ---")
            parts.append(self._format_goals(goals))
        
        # Conversation history
        if context.messages:
            parts.append("\n--- RECENT CONVERSATION ---")
            parts.append(context.get_history_text())
        
        # Current question
        parts.append(f"\n--- CURRENT QUESTION ---")
        parts.append(f"User: {question}")
        parts.append("\nPlease provide a helpful, personalized response based on the above context.")
        
        return "\n".join(parts)
    
    def _format_financial_data(self, record: FinancialRecord) -> str:
        """Format financial data for prompt."""
        return f"""
Monthly Income: ₹{record.monthly_income:,.2f}
Monthly Expenses: ₹{record.monthly_expenses:,.2f}
Savings Rate: {record.savings_rate:.1f}%

Assets:
- Cash/Savings: ₹{record.cash_savings:,.2f}
- Investments: ₹{record.investments:,.2f}
- Real Estate: ₹{record.real_estate:,.2f}
- Other Assets: ₹{record.other_assets:,.2f}
- Total Assets: ₹{record.total_assets:,.2f}

Liabilities:
- Credit Card Debt: ₹{record.credit_card_debt:,.2f}
- Student Loans: ₹{record.student_loans:,.2f}
- Personal Loans: ₹{record.personal_loans:,.2f}
- Mortgage: ₹{record.mortgage:,.2f}
- Other Liabilities: ₹{record.other_liabilities:,.2f}
- Total Liabilities: ₹{record.total_liabilities:,.2f}

Net Worth: ₹{record.net_worth:,.2f}
Debt-to-Income Ratio: {record.dti_ratio:.1f}%

Emergency Fund: ₹{record.emergency_fund_amount:,.2f} ({record.emergency_fund_progress:.1f}% of 6-month target)
Emergency Fund Status: {record.emergency_fund_status}
"""
    
    def _format_goals(self, goals: List[Goal]) -> str:
        """Format goals for prompt."""
        if not goals:
            return "No active goals."
        
        goal_texts = []
        for goal in goals:
            status = "✓ Completed" if goal.status == 'completed' else f"{goal.progress_percentage:.1f}% complete"
            goal_texts.append(
                f"- {goal.name}: ₹{goal.current_amount:,.2f} / ₹{goal.target_amount:,.2f} ({status})"
            )
        
        return "\n".join(goal_texts)
    
    def clear_history(self, user_id: int) -> bool:
        """
        Clear chat history for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if cleared successfully
        """
        if user_id in self._chat_contexts:
            del self._chat_contexts[user_id]
        return True
    
    def get_suggested_questions(
        self,
        financial_record: Optional[FinancialRecord] = None
    ) -> List[str]:
        """
        Get suggested questions based on financial profile.
        
        Args:
            financial_record: User's financial data
            
        Returns:
            List of suggested questions
        """
        suggestions = [
            "How can I improve my savings rate?",
            "Should I pay off debt or invest first?",
            "What's a good investment strategy for my situation?",
            "How much emergency fund do I need?",
            "Am I on track for my financial goals?"
        ]
        
        if financial_record:
            # Add contextual suggestions
            if financial_record.emergency_fund_status == 'Critical':
                suggestions.insert(0, "How can I build my emergency fund faster?")
            
            if financial_record.dti_ratio > 40:
                suggestions.insert(0, "What's the best strategy to reduce my debt?")
            
            if financial_record.savings_rate < 10:
                suggestions.insert(0, "How can I increase my savings with my current income?")
            
            if financial_record.investments < financial_record.total_assets * 0.2:
                suggestions.append("What investment options should I consider?")
        
        return suggestions[:5]
