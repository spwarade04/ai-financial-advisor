"""
Configuration module for AI Financial Advisor V2.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Base configuration class.
    """
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '86400'))  # 24 hours
    
    # AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-2.0-flash')
    
    # Frontend
    BACKEND_API_URL = os.getenv('BACKEND_API_URL', f'http://localhost:{FLASK_PORT}')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of missing required configuration variables
        """
        missing = []
        
        # Required in production
        if cls.FLASK_ENV == 'production':
            if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
                missing.append('SECRET_KEY (production default detected)')
            if cls.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
                missing.append('JWT_SECRET_KEY (production default detected)')
            if not cls.GEMINI_API_KEY:
                missing.append('GEMINI_API_KEY')
        
        return missing


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ai_financial_advisor_dev.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate production configuration."""
        missing = super().validate()
        
        if not cls.SQLALCHEMY_DATABASE_URI:
            missing.append('DATABASE_URL')
        
        return missing


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_config() -> Config:
    """
    Get configuration based on environment.
    
    Returns:
        Configuration instance
    """
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config_by_name.get(env, DevelopmentConfig)
    return config_class()
