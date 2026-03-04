"""
Backend server startup script for AI Financial Advisor V2.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

from backend import create_app
from config import get_config


def main():
    """Run the Flask backend server."""
    config = get_config()
    
    # Validate configuration
    missing = config.validate()
    if missing:
        print("=" * 60)
        print("CONFIGURATION WARNING")
        print("=" * 60)
        print(f"Missing or default configuration detected: {', '.join(missing)}")
        print("\nPlease check your .env file for proper configuration.")
        print("=" * 60)
        
        # Don't exit in development
        if config.FLASK_ENV == 'production':
            sys.exit(1)
        else:
            print("\nContinuing in development mode...")
    
    app = create_app(config)
    
    print("=" * 60)
    print("AI FINANCIAL ADVISOR V2 - BACKEND SERVER")
    print("=" * 60)
    print(f"Environment: {config.FLASK_ENV}")
    print(f"Debug Mode: {config.FLASK_DEBUG}")
    print(f"Server URL: http://localhost:{config.FLASK_PORT}")
    print("=" * 60)
    print("API Endpoints:")
    print(f"  Health Check:  GET  http://localhost:{config.FLASK_PORT}/api/health")
    print(f"  Register:      POST http://localhost:{config.FLASK_PORT}/auth/register")
    print(f"  Login:         POST http://localhost:{config.FLASK_PORT}/auth/login")
    print(f"  Analyze:       POST http://localhost:{config.FLASK_PORT}/api/analyze")
    print(f"  Emergency:     GET  http://localhost:{config.FLASK_PORT}/api/emergency-fund")
    print(f"  Net Worth:     GET  http://localhost:{config.FLASK_PORT}/api/net-worth")
    print(f"  Projection:    POST http://localhost:{config.FLASK_PORT}/api/projection")
    print(f"  Simulation:    POST http://localhost:{config.FLASK_PORT}/api/simulate")
    print(f"  Chat:          POST http://localhost:{config.FLASK_PORT}/api/chat")
    print(f"  Goals:         GET  http://localhost:{config.FLASK_PORT}/api/goals")
    print(f"  Admin:         GET  http://localhost:{config.FLASK_PORT}/admin/dashboard")
    print("=" * 60)
    print("Documentation:")
    print(f"  Swagger UI:    http://localhost:{config.FLASK_PORT}/docs/")
    print("=" * 60)
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()
