"""
Main API routes for AI Financial Advisor.
Includes financial analysis, projections, and new V2 features.
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from datetime import datetime

from backend.models.user_model import User
from backend.models.financial_record_model import FinancialRecord
from backend.models.goal_model import Goal
from backend.models.user_model import db

from backend.services.financial_service import FinancialService
from backend.services.goal_service import GoalService
from backend.services.ai_service import AIService
from backend.services.emergency_service import EmergencyFundService
from backend.services.networth_service import NetWorthService
from backend.services.simulation_service import SimulationService
from backend.services.chat_service import ChatService

from backend.utils.jwt_handler import get_jwt_handler
from backend.utils.logger import log_api_call, log_error

api_bp = Blueprint('api', __name__)
jwt_handler = get_jwt_handler()
chat_service = ChatService()


# ============================================================================
# Pydantic Models for Request Validation
# ============================================================================

class FinancialDataRequest(BaseModel):
    """Financial data submission request."""
    monthly_income: float = Field(..., gt=0, description="Monthly income")
    monthly_expenses: float = Field(..., ge=0, description="Monthly expenses")
    rent_expense: Optional[float] = Field(0, ge=0, description="Rent expense")
    utilities_expense: Optional[float] = Field(0, ge=0, description="Utilities expense")
    groceries_expense: Optional[float] = Field(0, ge=0, description="Groceries expense")
    transport_expense: Optional[float] = Field(0, ge=0, description="Transport expense")
    entertainment_expense: Optional[float] = Field(0, ge=0, description="Entertainment expense")
    other_expenses: Optional[float] = Field(0, ge=0, description="Other expenses")
    
    cash_savings: Optional[float] = Field(0, ge=0, description="Cash savings")
    investments: Optional[float] = Field(0, ge=0, description="Investments")
    real_estate: Optional[float] = Field(0, ge=0, description="Real estate value")
    other_assets: Optional[float] = Field(0, ge=0, description="Other assets")
    
    credit_card_debt: Optional[float] = Field(0, ge=0, description="Credit card debt")
    student_loans: Optional[float] = Field(0, ge=0, description="Student loans")
    personal_loans: Optional[float] = Field(0, ge=0, description="Personal loans")
    mortgage: Optional[float] = Field(0, ge=0, description="Mortgage")
    other_liabilities: Optional[float] = Field(0, ge=0, description="Other liabilities")
    
    emergency_fund_amount: Optional[float] = Field(0, ge=0, description="Emergency fund amount")


class GoalRequest(BaseModel):
    """Goal creation request."""
    name: str = Field(..., min_length=1, max_length=200, description="Goal name")
    description: Optional[str] = Field(None, max_length=500, description="Goal description")
    target_amount: float = Field(..., gt=0, description="Target amount")
    current_amount: Optional[float] = Field(0, ge=0, description="Current amount")
    target_date: Optional[str] = Field(None, description="Target date (ISO format)")
    goal_type: Optional[str] = Field('savings', description="Goal type")
    monthly_contribution: Optional[float] = Field(0, ge=0, description="Monthly contribution")
    expected_return_rate: Optional[float] = Field(0, ge=0, description="Expected annual return rate (decimal)")
    priority: Optional[str] = Field('medium', description="Priority: low, medium, high")


class ChatRequest(BaseModel):
    """Chat request."""
    question: str = Field(..., min_length=1, max_length=1000, description="User question")


class SimulationRequest(BaseModel):
    """Simulation request."""
    scenario: Optional[str] = Field(None, description="Predefined scenario key")
    custom_name: Optional[str] = Field(None, description="Custom scenario name")
    income_change: Optional[float] = Field(None, description="Income change percentage")
    expense_change: Optional[float] = Field(None, description="Expense change percentage")
    interest_rate_change: Optional[float] = Field(None, description="Interest rate change")


class ProjectionRequest(BaseModel):
    """Compound investment projection request."""
    principal: float = Field(..., gt=0, description="Initial investment amount")
    monthly_contribution: Optional[float] = Field(0, ge=0, description="Monthly contribution")
    annual_rate: Optional[float] = Field(0.08, ge=0, description="Annual return rate (decimal)")
    years: int = Field(..., gt=0, le=50, description="Investment period in years")
    compounds_per_year: Optional[int] = Field(12, ge=1, description="Compounding frequency per year")


# ============================================================================
# Health Check
# ============================================================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        - success: Boolean
        - message: Health status
        - timestamp: Current timestamp
    """
    return jsonify({
        'success': True,
        'message': 'AI Financial Advisor API is running',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============================================================================
# Financial Analysis
# ============================================================================

@api_bp.route('/analyze', methods=['POST'])
@jwt_handler.require_auth
def analyze_finances(current_user: User):
    """
    Analyze financial data and provide comprehensive insights.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        Financial data including income, expenses, assets, liabilities
    
    Returns:
        - success: Boolean
        - analysis: Comprehensive financial analysis
        - recommendations: AI-generated recommendations
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request
        try:
            financial_data = FinancialDataRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Create or update financial record
        record_data = financial_data.dict()
        record_data['total_assets'] = (
            record_data.get('cash_savings', 0) +
            record_data.get('investments', 0) +
            record_data.get('real_estate', 0) +
            record_data.get('other_assets', 0)
        )
        record_data['total_liabilities'] = (
            record_data.get('credit_card_debt', 0) +
            record_data.get('student_loans', 0) +
            record_data.get('personal_loans', 0) +
            record_data.get('mortgage', 0) +
            record_data.get('other_liabilities', 0)
        )
        
        # Save to database
        record = FinancialRecord(user_id=current_user.id, **record_data)
        db.session.add(record)
        db.session.commit()
        
        # Get AI analysis
        ai_service = AIService()
        analysis = ai_service.analyze_finances(record_data)
        
        return jsonify({
            'success': True,
            'data': {
                'financial_summary': record.to_dict(),
                'ai_analysis': analysis
            }
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/analyze', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during analysis'
        }), 500


@api_bp.route('/financial-records', methods=['GET'])
@jwt_handler.require_auth
def get_financial_records(current_user: User):
    """
    Get user's financial records history.
    
    Headers:
        - Authorization: Bearer <token>
    
    Query Parameters:
        - limit (int): Number of records to return (default: 10)
    
    Returns:
        - success: Boolean
        - records: List of financial records
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        records = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in records]
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/financial-records', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching records'
        }), 500


# ============================================================================
# Emergency Fund Analysis
# ============================================================================

@api_bp.route('/emergency-fund', methods=['GET'])
@jwt_handler.require_auth
def analyze_emergency_fund(current_user: User):
    """
    Analyze emergency fund status.
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - success: Boolean
        - data: Emergency fund analysis
    """
    try:
        # Get latest financial record
        record = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'No financial records found. Please submit your financial data first.'
            }), 404
        
        analysis = EmergencyFundService.analyze(record)
        
        return jsonify({
            'success': True,
            'data': EmergencyFundService.to_dict(analysis)
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/emergency-fund', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during analysis'
        }), 500


# ============================================================================
# Net Worth Tracking
# ============================================================================

@api_bp.route('/net-worth', methods=['GET'])
@jwt_handler.require_auth
def analyze_net_worth(current_user: User):
    """
    Analyze net worth and track growth.
    
    Headers:
        - Authorization: Bearer <token>
    
    Query Parameters:
        - months (int): History period in months (default: 12)
    
    Returns:
        - success: Boolean
        - data: Net worth analysis with historical data
    """
    try:
        months = request.args.get('months', 12, type=int)
        
        # Get latest financial record
        record = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'No financial records found. Please submit your financial data first.'
            }), 404
        
        analysis = NetWorthService.analyze(current_user.id, record, months)
        
        return jsonify({
            'success': True,
            'data': NetWorthService.to_dict(analysis)
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/net-worth', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during analysis'
        }), 500


# ============================================================================
# Compound Investment Projection
# ============================================================================

@api_bp.route('/projection', methods=['POST'])
@jwt_handler.require_auth
def calculate_projection(current_user: User):
    """
    Calculate compound investment projection.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        - principal: Initial investment
        - monthly_contribution: Monthly addition
        - annual_rate: Expected annual return
        - years: Investment period
    
    Returns:
        - success: Boolean
        - data: Projection results with yearly breakdown
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request
        try:
            proj_data = ProjectionRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Calculate projections for different scenarios
        scenarios = []
        rates = [
            ('Conservative (6%)', 0.06),
            ('Moderate (8%)', 0.08),
            ('Aggressive (12%)', 0.12),
            ('High Growth (15%)', 0.15)
        ]
        
        for name, rate in rates:
            # Compound interest formula: A = P(1 + r/n)^(nt) + PMT * (((1 + r/n)^(nt) - 1) / (r/n))
            n = proj_data.compounds_per_year
            t = proj_data.years
            r = rate
            P = proj_data.principal
            PMT = proj_data.monthly_contribution
            
            # Calculate future value
            compound_factor = (1 + r/n) ** (n*t)
            fv_principal = P * compound_factor
            
            if r > 0:
                fv_contributions = PMT * ((compound_factor - 1) / (r/n))
            else:
                fv_contributions = PMT * n * t
            
            total_fv = fv_principal + fv_contributions
            total_contributions = P + (PMT * 12 * t)
            interest_earned = total_fv - total_contributions
            
            # Year-by-year breakdown
            yearly_data = []
            for year in range(1, t + 1):
                year_factor = (1 + r/n) ** (n*year)
                year_principal = P * year_factor
                if r > 0:
                    year_contrib = PMT * ((year_factor - 1) / (r/n))
                else:
                    year_contrib = PMT * n * year
                yearly_data.append({
                    'year': year,
                    'value': round(year_principal + year_contrib, 2),
                    'contributions': P + (PMT * 12 * year),
                    'interest_earned': round(year_principal + year_contrib - P - (PMT * 12 * year), 2)
                })
            
            scenarios.append({
                'name': name,
                'rate': rate,
                'final_value': round(total_fv, 2),
                'total_contributions': round(total_contributions, 2),
                'interest_earned': round(interest_earned, 2),
                'yearly_breakdown': yearly_data
            })
        
        return jsonify({
            'success': True,
            'data': {
                'input': {
                    'principal': proj_data.principal,
                    'monthly_contribution': proj_data.monthly_contribution,
                    'years': proj_data.years
                },
                'scenarios': scenarios
            }
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/projection', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during projection'
        }), 500


# ============================================================================
# Risk Simulation
# ============================================================================

@api_bp.route('/simulations', methods=['GET'])
@jwt_handler.require_auth
def get_simulation_scenarios(current_user: User):
    """
    Get available simulation scenarios.
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - success: Boolean
        - data: List of available scenarios
    """
    return jsonify({
        'success': True,
        'data': SimulationService.get_available_scenarios()
    }), 200


@api_bp.route('/simulate', methods=['POST'])
@jwt_handler.require_auth
def run_simulation(current_user: User):
    """
    Run financial risk simulation.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        - scenario: Predefined scenario key (optional)
        - Or custom scenario parameters
    
    Returns:
        - success: Boolean
        - data: Simulation results
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Get latest financial record
        record = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'No financial records found. Please submit your financial data first.'
            }), 404
        
        # Run simulation
        scenario_key = data.get('scenario')
        
        if scenario_key:
            result = SimulationService.run_simulation(record, scenario_key)
        else:
            # Validate custom scenario
            try:
                sim_data = SimulationRequest(**data)
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'error': 'Validation Error',
                    'message': str(e)
                }), 400
            
            result = SimulationService.run_custom_simulation(
                record,
                sim_data.custom_name or 'Custom Scenario',
                sim_data.income_change or 0,
                sim_data.expense_change or 0,
                sim_data.interest_rate_change or 0
            )
        
        return jsonify({
            'success': True,
            'data': SimulationService.to_dict(result)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    except Exception as e:
        log_error(e, {'endpoint': '/api/simulate', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during simulation'
        }), 500


# ============================================================================
# AI Chat
# ============================================================================

@api_bp.route('/chat', methods=['POST'])
@jwt_handler.require_auth
def chat(current_user: User):
    """
    AI Financial Chat - Get personalized financial advice.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        - question: User's question
    
    Returns:
        - success: Boolean
        - answer: AI response
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request
        try:
            chat_data = ChatRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Get user's financial data
        record = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        goals = Goal.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).all()
        
        # Get AI response
        result = chat_service.chat(
            user_id=current_user.id,
            question=chat_data.question,
            financial_record=record,
            goals=goals
        )
        
        if not result['success']:
            return jsonify(result), 503
        
        return jsonify(result), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/chat', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while processing your question'
        }), 500


@api_bp.route('/chat/suggestions', methods=['GET'])
@jwt_handler.require_auth
def get_chat_suggestions(current_user: User):
    """
    Get suggested questions for AI chat.
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - success: Boolean
        - suggestions: List of suggested questions
    """
    try:
        # Get user's financial data
        record = FinancialRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(FinancialRecord.record_date.desc()).first()
        
        suggestions = chat_service.get_suggested_questions(record)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/chat/suggestions', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred'
        }), 500


@api_bp.route('/chat/clear', methods=['POST'])
@jwt_handler.require_auth
def clear_chat_history(current_user: User):
    """
    Clear chat conversation history.
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - success: Boolean
        - message: Confirmation message
    """
    chat_service.clear_history(current_user.id)
    
    return jsonify({
        'success': True,
        'message': 'Chat history cleared successfully'
    }), 200


# ============================================================================
# Goals Management
# ============================================================================

@api_bp.route('/goals', methods=['GET'])
@jwt_handler.require_auth
def get_goals(current_user: User):
    """
    Get user's financial goals.
    
    Headers:
        - Authorization: Bearer <token>
    
    Query Parameters:
        - status (str): Filter by status (active, completed, etc.)
    
    Returns:
        - success: Boolean
        - data: List of goals
    """
    try:
        status_filter = request.args.get('status')
        
        query = Goal.query.filter_by(user_id=current_user.id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        goals = query.order_by(Goal.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [goal.to_dict() for goal in goals]
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/goals', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching goals'
        }), 500


@api_bp.route('/goals', methods=['POST'])
@jwt_handler.require_auth
def create_goal(current_user: User):
    """
    Create a new financial goal.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        Goal details
    
    Returns:
        - success: Boolean
        - data: Created goal
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request
        try:
            goal_data = GoalRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Parse target date if provided
        target_date = None
        if goal_data.target_date:
            try:
                target_date = datetime.fromisoformat(goal_data.target_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Validation Error',
                    'message': 'Invalid target_date format. Use ISO format (YYYY-MM-DD)'
                }), 400
        
        # Create goal
        goal = Goal(
            user_id=current_user.id,
            name=goal_data.name,
            description=goal_data.description,
            target_amount=goal_data.target_amount,
            current_amount=goal_data.current_amount,
            target_date=target_date,
            goal_type=goal_data.goal_type,
            monthly_contribution=goal_data.monthly_contribution,
            expected_return_rate=goal_data.expected_return_rate,
            priority=goal_data.priority
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal created successfully',
            'data': goal.to_dict()
        }), 201
        
    except Exception as e:
        log_error(e, {'endpoint': '/api/goals', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while creating goal'
        }), 500


@api_bp.route('/goals/<int:goal_id>', methods=['GET'])
@jwt_handler.require_auth
def get_goal(current_user: User, goal_id: int):
    """
    Get a specific goal.
    
    Headers:
        - Authorization: Bearer <token>
    
    Path Parameters:
        - goal_id: Goal ID
    
    Returns:
        - success: Boolean
        - data: Goal details
    """
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        
        if not goal:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'Goal not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': goal.to_dict()
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': f'/api/goals/{goal_id}', 'user_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred'
        }), 500


@api_bp.route('/goals/<int:goal_id>', methods=['PUT'])
@jwt_handler.require_auth
def update_goal(current_user: User, goal_id: int):
    """
    Update a goal.
    
    Headers:
        - Authorization: Bearer <token>
    
    Path Parameters:
        - goal_id: Goal ID
    
    Request Body:
        Updated goal fields
    
    Returns:
        - success: Boolean
        - data: Updated goal
    """
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        
        if not goal:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'Goal not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'target_amount', 'current_amount',
            'target_date', 'goal_type', 'monthly_contribution',
            'expected_return_rate', 'priority', 'status'
        ]
        
        for field in allowed_fields:
            if field in data:
                if field == 'target_date' and data[field]:
                    try:
                        setattr(goal, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'error': 'Validation Error',
                            'message': 'Invalid target_date format'
                        }), 400
                else:
                    setattr(goal, field, data[field])
        
        # Check if goal is completed
        if goal.current_amount >= goal.target_amount and goal.status != 'completed':
            goal.complete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal updated successfully',
            'data': goal.to_dict()
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': f'/api/goals/{goal_id}', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while updating goal'
        }), 500


@api_bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@jwt_handler.require_auth
def delete_goal(current_user: User, goal_id: int):
    """
    Delete a goal.
    
    Headers:
        - Authorization: Bearer <token>
    
    Path Parameters:
        - goal_id: Goal ID
    
    Returns:
        - success: Boolean
        - message: Confirmation
    """
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        
        if not goal:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'Goal not found'
            }), 404
        
        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal deleted successfully'
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': f'/api/goals/{goal_id}', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while deleting goal'
        }), 500


@api_bp.route('/goals/<int:goal_id>/contribute', methods=['POST'])
@jwt_handler.require_auth
def contribute_to_goal(current_user: User, goal_id: int):
    """
    Add contribution to a goal.
    
    Headers:
        - Authorization: Bearer <token>
    
    Path Parameters:
        - goal_id: Goal ID
    
    Request Body:
        - amount: Contribution amount
    
    Returns:
        - success: Boolean
        - data: Updated goal
    """
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        
        if not goal:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'Goal not found'
            }), 404
        
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Contribution amount required'
            }), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Contribution amount must be positive'
            }), 400
        
        goal.current_amount += amount
        
        # Check if goal is completed
        if goal.current_amount >= goal.target_amount:
            goal.complete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Added ₹{amount:,.2f} to goal',
            'data': goal.to_dict()
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': f'/api/goals/{goal_id}/contribute', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred'
        }), 500
