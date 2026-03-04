"""
JWT Authentication Handler.
Manages token generation, validation, and user authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from backend.models.user_model import User


class JWTHandler:
    """
    Handler for JWT token operations.
    """
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256'):
        """
        Initialize JWT handler.
        
        Args:
            secret_key: JWT secret key (defaults to env var or fallback)
            algorithm: JWT algorithm
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = algorithm
        self.access_token_expire = timedelta(hours=24)
        self.refresh_token_expire = timedelta(days=7)
    
    def generate_token(self, user_id: int, token_type: str = 'access') -> str:
        """
        Generate JWT token for user.
        
        Args:
            user_id: User ID to encode in token
            token_type: Type of token ('access' or 'refresh')
            
        Returns:
            Encoded JWT token
        """
        expire_delta = self.access_token_expire if token_type == 'access' else self.refresh_token_expire
        
        payload = {
            'user_id': user_id,
            'token_type': token_type,
            'exp': datetime.utcnow() + expire_delta,
            'iat': datetime.utcnow(),
            'jti': f"{user_id}-{datetime.utcnow().timestamp()}"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token_from_header(self) -> Optional[str]:
        """
        Extract token from Authorization header.
        
        Returns:
            Token string or None
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    def get_current_user(self) -> Optional[User]:
        """
        Get current authenticated user from token.
        
        Returns:
            User object or None
        """
        token = self.get_token_from_header()
        if not token:
            return None
        
        payload = self.decode_token(token)
        if not payload or payload.get('token_type') != 'access':
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        return User.query.get(user_id)
    
    def require_auth(self, f):
        """
        Decorator to require authentication for a route.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            user = self.get_current_user()
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': 'Valid authentication token required'
                }), 401
            
            # Add user to kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated
    
    def require_admin(self, f):
        """
        Decorator to require admin privileges for a route.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            user = self.get_current_user()
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': 'Valid authentication token required'
                }), 401
            
            if not user.is_admin:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'Admin privileges required'
                }), 403
            
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated


# Global JWT handler instance
jwt_handler = JWTHandler()


def get_jwt_handler() -> JWTHandler:
    """
    Get JWT handler instance.
    
    Returns:
        JWTHandler instance
    """
    return jwt_handler
