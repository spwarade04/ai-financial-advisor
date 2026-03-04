"""
Logging utility for AI Financial Advisor.
Provides structured logging for API calls, errors, and system events.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
from flask import request, g


class StructuredLogFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def get_logger(name: str = 'ai_financial_advisor') -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(console_handler)
        
        # File handler for errors
        file_handler = logging.FileHandler('logs/error.log')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(file_handler)
        
        # File handler for all logs
        app_file_handler = logging.FileHandler('logs/app.log')
        app_file_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(app_file_handler)
        
        logger.setLevel(logging.INFO)
    
    return logger


def log_api_call(f):
    """
    Decorator to log API calls with timing and metadata.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.utcnow()
        
        # Get request info
        endpoint = request.endpoint
        method = request.method
        path = request.path
        
        try:
            # Execute function
            response = f(*args, **kwargs)
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Get status code
            status_code = response[1] if isinstance(response, tuple) else 200
            
            # Create log record
            extra = {
                'endpoint': endpoint or path,
                'method': method,
                'duration_ms': round(duration, 2),
                'status_code': status_code,
                'user_id': getattr(g, 'user_id', None),
                'request_id': getattr(g, 'request_id', None)
            }
            
            logger.info(
                f'API Call: {method} {path} - {status_code} ({duration:.2f}ms)',
                extra={'extra_data': extra}
            )
            
            return response
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            extra = {
                'endpoint': endpoint or path,
                'method': method,
                'duration_ms': round(duration, 2),
                'error': str(e),
                'user_id': getattr(g, 'user_id', None),
                'request_id': getattr(g, 'request_id', None)
            }
            
            logger.error(
                f'API Error: {method} {path} - {str(e)}',
                extra={'extra_data': extra},
                exc_info=True
            )
            raise
    
    return decorated


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with context.
    
    Args:
        error: Exception to log
        context: Additional context data
    """
    logger = get_logger()
    
    log_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {}
    }
    
    logger.error(
        f'Error: {type(error).__name__}: {str(error)}',
        extra={'extra_data': log_data},
        exc_info=True
    )


def log_auth_attempt(username: str, success: bool, ip_address: str) -> None:
    """
    Log authentication attempt.
    
    Args:
        username: Username attempting login
        success: Whether login was successful
        ip_address: IP address of request
    """
    logger = get_logger()
    
    log_data = {
        'username': username,
        'success': success,
        'ip_address': ip_address,
        'event': 'auth_attempt'
    }
    
    if success:
        logger.info(f'Login successful: {username}', extra={'extra_data': log_data})
    else:
        logger.warning(f'Login failed: {username}', extra={'extra_data': log_data})


def log_ai_api_call(model: str, prompt_length: int, success: bool, duration_ms: float) -> None:
    """
    Log AI API call.
    
    Args:
        model: AI model used
        prompt_length: Length of prompt
        success: Whether call was successful
        duration_ms: Duration in milliseconds
    """
    logger = get_logger()
    
    log_data = {
        'model': model,
        'prompt_length': prompt_length,
        'success': success,
        'duration_ms': round(duration_ms, 2),
        'event': 'ai_api_call'
    }
    
    if success:
        logger.info(f'AI API call successful: {model}', extra={'extra_data': log_data})
    else:
        logger.error(f'AI API call failed: {model}', extra={'extra_data': log_data})


# Ensure logs directory exists
import os
os.makedirs('logs', exist_ok=True)
