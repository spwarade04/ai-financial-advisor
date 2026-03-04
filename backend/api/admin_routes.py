"""
Admin routes for system management and analytics.
"""

from flask import Blueprint, request, jsonify
from backend.models.user_model import User
from backend.services.admin_service import AdminService
from backend.utils.jwt_handler import get_jwt_handler
from backend.utils.logger import log_error

admin_bp = Blueprint('admin', __name__)
jwt_handler = get_jwt_handler()


@admin_bp.route('/users', methods=['GET'])
@jwt_handler.require_admin
def get_users(current_user: User):
    """
    Get paginated list of all users (Admin only).
    
    Headers:
        - Authorization: Bearer <admin_token>
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20)
        - search (str): Search term for username/email
    
    Returns:
        - success: Boolean
        - users: List of user data
        - pagination: Pagination metadata
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', None)
        
        result = AdminService.get_all_users(
            page=page,
            per_page=per_page,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/admin/users', 'admin_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching users'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_handler.require_admin
def get_user_details(current_user: User, user_id: int):
    """
    Get detailed information about a specific user (Admin only).
    
    Headers:
        - Authorization: Bearer <admin_token>
    
    Path Parameters:
        - user_id (int): User ID
    
    Returns:
        - success: Boolean
        - data: User details
    """
    try:
        result = AdminService.get_user_details(user_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': f'/admin/users/{user_id}', 'admin_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while fetching user details'
        }), 500


@admin_bp.route('/risk-summary', methods=['GET'])
@jwt_handler.require_admin
def get_risk_summary(current_user: User):
    """
    Get system-wide risk summary (Admin only).
    
    Headers:
        - Authorization: Bearer <admin_token>
    
    Returns:
        - success: Boolean
        - data: Risk distribution and health metrics
    """
    try:
        result = AdminService.get_risk_summary()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/admin/risk-summary', 'admin_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while generating risk summary'
        }), 500


@admin_bp.route('/analytics', methods=['GET'])
@jwt_handler.require_admin
def get_analytics(current_user: User):
    """
    Get comprehensive system analytics (Admin only).
    
    Headers:
        - Authorization: Bearer <admin_token>
    
    Returns:
        - success: Boolean
        - data: System analytics
    """
    try:
        analytics = AdminService.get_system_analytics()
        result = AdminService.to_dict_analytics(analytics)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/admin/analytics', 'admin_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while generating analytics'
        }), 500


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_handler.require_admin
def get_dashboard(current_user: User):
    """
    Get admin dashboard data (Admin only).
    
    Headers:
        - Authorization: Bearer <admin_token>
    
    Returns:
        - success: Boolean
        - data: Combined dashboard data
    """
    try:
        # Get all dashboard data
        users_data = AdminService.get_all_users(page=1, per_page=5)
        risk_summary = AdminService.get_risk_summary()
        analytics = AdminService.get_system_analytics()
        
        return jsonify({
            'success': True,
            'data': {
                'overview': AdminService.to_dict_analytics(analytics),
                'risk_summary': risk_summary,
                'recent_users': users_data
            }
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/admin/dashboard', 'admin_id': current_user.id})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while generating dashboard data'
        }), 500
