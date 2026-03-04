"""
Authentication routes for user registration and login.
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field, validator, ValidationError
from backend.models.user_model import User, db
from backend.utils.jwt_handler import get_jwt_handler
from backend.utils.logger import log_auth_attempt, log_error

auth_bp = Blueprint('auth', __name__)
jwt_handler = get_jwt_handler()


class RegisterRequest(BaseModel):
    """Registration request validation model."""
    username: str = Field(..., min_length=3, max_length=80, description="Username for the account")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower()


class LoginRequest(BaseModel):
    """Login request validation model."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request Body:
        - username (str): Unique username (3-80 characters)
        - email (str): Valid email address
        - password (str): Password (minimum 6 characters)
    
    Returns:
        - success: Boolean indicating registration status
        - message: Success or error message
        - user: User data (on success)
        - token: JWT access token (on success)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request data
        try:
            register_data = RegisterRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Check if username exists
        if User.query.filter_by(username=register_data.username).first():
            return jsonify({
                'success': False,
                'error': 'Conflict',
                'message': 'Username already exists'
            }), 409
        
        # Check if email exists
        if User.query.filter_by(email=register_data.email).first():
            return jsonify({
                'success': False,
                'error': 'Conflict',
                'message': 'Email already registered'
            }), 409
        
        # Create new user
        new_user = User(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        access_token = jwt_handler.generate_token(new_user.id, 'access')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        log_error(e, {'endpoint': '/auth/register'})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during registration'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and generate JWT token.
    
    Request Body:
        - username (str): Username or email
        - password (str): Password
    
    Returns:
        - success: Boolean indicating login status
        - message: Success or error message
        - user: User data (on success)
        - token: JWT access token (on success)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        # Validate request data
        try:
            login_data = LoginRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == login_data.username) | (User.email == login_data.username)
        ).first()
        
        # Get IP address
        ip_address = request.remote_addr or 'unknown'
        
        # Verify password
        if not user or not user.verify_password(login_data.password):
            log_auth_attempt(login_data.username, False, ip_address)
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Invalid username or password'
            }), 401
        
        # Update last login
        user.update_last_login()
        
        # Log successful login
        log_auth_attempt(user.username, True, ip_address)
        
        # Generate token
        access_token = jwt_handler.generate_token(user.id, 'access')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/auth/login'})
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred during login'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_handler.require_auth
def get_profile(current_user: User):
    """
    Get current user profile.
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - success: Boolean
        - user: User profile data
    """
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_handler.require_auth
def change_password(current_user: User):
    """
    Change user password.
    
    Headers:
        - Authorization: Bearer <token>
    
    Request Body:
        - current_password (str): Current password
        - new_password (str): New password (minimum 6 characters)
    
    Returns:
        - success: Boolean
        - message: Success or error message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body required'
            }), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Current password and new password required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'New password must be at least 6 characters'
            }), 400
        
        # Verify current password
        if not current_user.verify_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Current password is incorrect'
            }), 401
        
        # Update password
        current_user.password_hash = current_user._hash_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        log_error(e, {'endpoint': '/auth/change-password', 'user_id': current_user.id})
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An error occurred while changing password'
        }), 500
