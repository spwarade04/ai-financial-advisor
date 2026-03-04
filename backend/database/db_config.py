"""
Database configuration module.
Handles database connection setup and initialization.
"""

import os
from typing import Optional
from flask import Flask
from backend.models.user_model import db
from backend.models.financial_record_model import FinancialRecord
from backend.models.goal_model import Goal


def get_db_uri() -> str:
    """
    Get database URI based on environment.
    
    Returns:
        Database connection string
    """
    # Check for PostgreSQL configuration
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # PostgreSQL individual parameters
    pg_host = os.getenv('POSTGRES_HOST')
    if pg_host:
        pg_user = os.getenv('POSTGRES_USER', 'postgres')
        pg_password = os.getenv('POSTGRES_PASSWORD', '')
        pg_db = os.getenv('POSTGRES_DB', 'ai_financial_advisor')
        pg_port = os.getenv('POSTGRES_PORT', '5432')
        return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    
    # Default to SQLite for development
    return 'sqlite:///ai_financial_advisor.db'


def init_db(app: Flask, db_uri: Optional[str] = None) -> None:
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application instance
        db_uri: Optional database URI override
    """
    if db_uri is None:
        db_uri = get_db_uri()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        create_default_admin()


def create_default_admin() -> None:
    """
    Create default admin user if no users exist.
    """
    from backend.models.user_model import User
    
    # Check if any users exist
    if User.query.first() is None:
        admin_user = User(
            username='admin',
            email='admin@aifinancialadvisor.com',
            password='admin123',  # Change in production!
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()


def get_db_session():
    """
    Get database session.
    
    Returns:
        SQLAlchemy session
    """
    return db.session


def close_db_session() -> None:
    """Close database session."""
    db.session.remove()
