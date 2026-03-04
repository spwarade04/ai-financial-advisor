# AI Financial Advisor

An intelligent, modular financial planning system that delivers personalized, data-driven financial advice using Google's Gemini Flash generative AI model.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

The AI Financial Advisor is designed for:
- **Students** - Learn financial planning basics
- **Working Professionals** - Optimize savings and investments
- **Retirees** - Manage wealth and plan legacy

### Key Features

- **Budget Analysis** - Comprehensive spending pattern analysis
- **Savings Optimization** - Smart strategies to maximize savings
- **Debt Management** - Strategic debt repayment plans
- **Goal Planning** - Achieve financial goals with SIP projections
- **Portfolio Allocation** - Risk-based investment recommendations
- **AI Recommendations** - Personalized financial roadmap powered by Gemini Flash

## Architecture

```
User (Streamlit UI)
        ↓
Flask REST API
        ↓
Service Layer
   - Financial Analysis Service
   - Goal Planning Service
   - AI Recommendation Service
        ↓
Gemini API
        ↓
JSON Response
        ↓
Dashboard Visualization
```

### System Components

1. **Frontend (Streamlit)** - Interactive web dashboard
2. **Backend (Flask)** - REST API with service-based architecture
3. **AI Service** - Google Gemini Flash integration
4. **Financial Engine** - Pandas/NumPy calculations
5. **Visualization** - Plotly charts and graphs

## Project Structure

```
AI-Financial-Advisor/
│
├── app.py                      # Main CLI entry point
├── run_backend.py              # Backend server startup
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example                # Environment variables template
│
├── backend/
│   ├── __init__.py            # Flask app factory
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # REST API endpoints
│   │
│   ├── services/
│   │   ├── financial_service.py   # Financial calculations
│   │   ├── goal_service.py        # Goal planning & SIP
│   │   └── ai_service.py          # Gemini AI integration
│   │
│   ├── models/
│   │   └── financial_model.py     # Data models
│   │
│   └── utils/
│       └── helpers.py             # Utility functions
│
├── frontend/
│   └── dashboard.py           # Streamlit application
│
├── tests/
│   ├── test_financial_service.py
│   └── test_goal_service.py
│
└── assets/
    └── logo.png
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Financial-Advisor
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
BACKEND_API_URL=http://localhost:5000
```

**Get your Gemini API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

## How to Run

### Option 1: Run Backend and Frontend Separately

**Terminal 1 - Start Backend:**
```bash
python run_backend.py
```

The backend will start at `http://localhost:5000`

**Terminal 2 - Start Frontend:**
```bash
python -m streamlit run frontend/dashboard.py
```

The frontend will open at `http://localhost:8501`

### Option 2: Using the CLI

```bash
# Run backend only
python app.py backend

# Run frontend only
python app.py frontend
```

## API Documentation

### POST /api/analyze

Analyzes financial data and returns comprehensive recommendations.

**Request:**
```json
{
  "income": 60000,
  "expenses": 35000,
  "savings": 100000,
  "debt": 50000,
  "goal_amount": 500000,
  "goal_years": 3,
  "risk_level": "Medium"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "financial_metrics": {
      "income": 60000.0,
      "expenses": 35000.0,
      "savings": 100000.0,
      "debt": 50000.0,
      "monthly_surplus": 25000.0,
      "budget_ratio": 0.5833,
      "savings_rate": 0.4167,
      "debt_to_income_ratio": 0.8333,
      "financial_health_score": 65.5
    },
    "goal_plan": {
      "goal_amount": 500000.0,
      "goal_years": 3,
      "monthly_savings_required": 8500.5,
      "projected_amount": 520000.0,
      "expected_return_rate": 0.12,
      "portfolio_allocation": {
        "Equity": 50,
        "Mutual Funds": 30,
        "Bonds": 20
      },
      "feasibility": "achievable"
    },
    "risk_classification": {
      "classification": "Moderate",
      "description": "Your debt-to-income ratio is manageable...",
      "recommendations": [...]
    },
    "ai_recommendation": "## EXECUTIVE SUMMARY\n\nBased on your financial profile..."
  }
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "service": "AI Financial Advisor API"
}
```

### GET /api/portfolio/{risk_level}

Get portfolio allocation for a risk level.

**Response:**
```json
{
  "success": true,
  "data": {
    "risk_level": "Medium",
    "allocation": {
      "Equity": 50,
      "Mutual Funds": 30,
      "Bonds": 20
    }
  }
}
```

## Financial Calculations

### Budget Ratio
```
Budget Ratio = Monthly Expenses / Monthly Income
```

### Savings Rate
```
Savings Rate = Monthly Savings / Monthly Income
```

### Debt-to-Income (DTI) Ratio
```
DTI = Total Debt / Annual Income
```

### Financial Health Score (0-100)
- Savings Rate: 40% weight
- DTI Ratio: 35% weight
- Budget Ratio: 25% weight

### SIP Projection
```
FV = P × (1 + r)^n + PMT × [((1 + r)^n - 1) / r] × (1 + r)
```
Where:
- FV = Future Value
- P = Principal (current savings)
- PMT = Monthly investment
- r = Monthly return rate
- n = Number of months

## Portfolio Allocation Rules

| Risk Level | Equity | Mutual Funds | Bonds | Expected Return |
|------------|--------|--------------|-------|-----------------|
| Low        | 10%    | 30%          | 60%   | ~8% annually    |
| Medium     | 50%    | 30%          | 20%   | ~12% annually   |
| High       | 70%    | 20%          | 10%   | ~16% annually   |

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_financial_service.py -v
pytest tests/test_goal_service.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

## Deployment

### Local Deployment

1. Follow setup instructions above
2. Run backend: `python run_backend.py`
3. Run frontend: `streamlit run frontend/dashboard.py`

### Production Deployment

**Backend (Flask):**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn -w 4 -b 0.0.0.0:5000 "backend:create_app()"
```

**Frontend (Streamlit):**
```bash
streamlit run frontend/dashboard.py --server.port=8501 --server.address=0.0.0.0
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000 8501

CMD ["python", "run_backend.py"]
```

Build and run:
```bash
docker build -t ai-financial-advisor .
docker run -p 5000:5000 -p 8501:8501 ai-financial-advisor
```

## Future Enhancements

### Predictive Analytics
- Machine learning models for expense prediction
- Income forecasting based on historical data
- Market trend analysis for investment recommendations

### Risk Simulation
- Monte Carlo simulations for portfolio performance
- Stress testing under various market conditions
- Scenario analysis (recession, inflation, etc.)

### Multi-User Dashboard
- User authentication and profiles
- Family financial planning
- Advisor-client collaboration features

### Additional Features
- Tax optimization strategies
- Retirement planning calculator
- EMI vs. Investment comparison
- Real-time market data integration
- Mobile app companion

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | Flask |
| AI Model | Google Gemini Flash |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Validation | Pydantic |
| Testing | Pytest |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This application provides general financial guidance and educational information. It is not a substitute for professional financial advice. Please consult with a certified financial advisor before making investment decisions. Past performance does not guarantee future results.

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Built with ❤️ using Python, Flask, Streamlit, and Google Gemini**
