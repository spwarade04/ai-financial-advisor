"""
Main entry point for AI Financial Advisor V2.
Provides command-line interface to run backend or frontend.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_backend():
    """Run the Flask backend server."""
    subprocess.run([sys.executable, "run_backend.py"])


def run_frontend():
    """Run the Streamlit frontend."""
    frontend_path = Path(__file__).parent / "frontend" / "dashboard.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(frontend_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])


def run_tests():
    """Run the test suite."""
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def init_database():
    """Initialize the database."""
    from backend import create_app
    from backend.database.db_config import init_db
    
    app = create_app()
    with app.app_context():
        print("Database initialized successfully!")


def main():
    """Main entry point with CLI."""
    parser = argparse.ArgumentParser(
        description="AI Financial Advisor V2 - Advanced FinTech System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py backend       # Start the backend server
  python app.py frontend      # Start the frontend dashboard
  python app.py test          # Run tests
  python app.py init-db       # Initialize database

For more information, visit: http://localhost:5000/docs/
        """
    )
    
    parser.add_argument(
        "command",
        choices=["backend", "frontend", "test", "init-db"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "backend":
        print("Starting AI Financial Advisor V2 Backend...")
        run_backend()
    elif args.command == "frontend":
        print("Starting AI Financial Advisor V2 Frontend...")
        run_frontend()
    elif args.command == "test":
        print("Running tests...")
        run_tests()
    elif args.command == "init-db":
        print("Initializing database...")
        init_database()


if __name__ == '__main__':
    main()
