"""
Backend package for AI Financial Advisor V2.
Flask application factory pattern implementation.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from backend.database.db_config import init_db


def create_app(config: Config = None) -> Flask:
    """
    Application factory for creating Flask app instances.
    
    Args:
        config: Configuration object. If None, uses default config.
        
    Returns:
        Configured Flask application instance.
    """
    if config is None:
        from config import get_config
        config = get_config()
    
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/auth/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/admin/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from backend.api.routes import api_bp
    from backend.api.auth_routes import auth_bp
    from backend.api.admin_routes import admin_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Error handlers
    register_error_handlers(app)
    
    # Swagger documentation
    register_swagger(app)
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The requested method is not allowed for this resource'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def register_swagger(app: Flask) -> None:
    """Register Swagger documentation."""
    try:
        from flasgger import Swagger
        
        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec",
                    "route": "/apispec.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs/",
            "title": "AI Financial Advisor API",
            "version": "2.0.0",
            "description": """
            AI Financial Advisor API V2
            
            Advanced FinTech system with:
            - User authentication (JWT)
            - Financial analysis and tracking
            - Emergency fund analyzer
            - Net worth tracking
            - Compound investment projections
            - Risk simulation engine
            - AI financial chat
            - Goal management
            - Admin dashboard
            
            Authentication:
            Most endpoints require a Bearer token in the Authorization header.
            Obtain a token by calling POST /auth/login
            """,
            "termsOfService": "",
            "contact": {
                "name": "AI Financial Advisor Support",
                "email": "support@aifinancialadvisor.com"
            }
        }
        
        Swagger(app, config=swagger_config)
        
    except ImportError:
        app.logger.warning("Flasgger not installed. Swagger documentation disabled.")
