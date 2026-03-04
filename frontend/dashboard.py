"""
AI Financial Advisor V2 - Streamlit Frontend Dashboard.
Advanced FinTech interface with authentication and comprehensive features.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="AI Financial Advisor V2",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-critical {
        color: #dc3545;
        font-weight: bold;
    }
    .risk-moderate {
        color: #ffc107;
        font-weight: bold;
    }
    .risk-safe {
        color: #28a745;
        font-weight: bold;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.token is not None


def get_headers():
    """Get request headers with authentication."""
    headers = {'Content-Type': 'application/json'}
    if st.session_state.token:
        headers['Authorization'] = f'Bearer {st.session_state.token}'
    return headers


def logout():
    """Logout user."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.page = 'login'
    st.session_state.chat_history = []


# ============================================================================
# API Helper Functions
# ============================================================================

def api_get(endpoint):
    """Make authenticated GET request."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=get_headers())
        return response.json(), response.status_code
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


def api_post(endpoint, data=None):
    """Make authenticated POST request."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            json=data
        )
        return response.json(), response.status_code
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


def api_put(endpoint, data=None):
    """Make authenticated PUT request."""
    try:
        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            json=data
        )
        return response.json(), response.status_code
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


def api_delete(endpoint):
    """Make authenticated DELETE request."""
    try:
        response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=get_headers())
        return response.json(), response.status_code
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500


# ============================================================================
# Authentication Pages
# ============================================================================

def login_page():
    """Display login page."""
    st.markdown('<h1 class="main-header">💰 AI Financial Advisor V2</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    result, status = api_post('/auth/login', {
                        'username': username,
                        'password': password
                    })
                    
                    if result.get('success'):
                        st.session_state.token = result['token']
                        st.session_state.user = result['user']
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error(result.get('message', 'Login failed'))
                else:
                    st.warning("Please enter username and password")
        
        with tab2:
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register", use_container_width=True):
                if new_username and new_email and new_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        result, status = api_post('/auth/register', {
                            'username': new_username,
                            'email': new_email,
                            'password': new_password
                        })
                        
                        if result.get('success'):
                            st.session_state.token = result['token']
                            st.session_state.user = result['user']
                            st.session_state.page = 'dashboard'
                            st.success("Registration successful!")
                            st.rerun()
                        else:
                            st.error(result.get('message', 'Registration failed'))
                else:
                    st.warning("Please fill in all fields")


# ============================================================================
# Dashboard Components
# ============================================================================

def sidebar():
    """Display sidebar navigation."""
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.get('username', 'User')}")
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("💵 Financial Analysis", use_container_width=True):
            st.session_state.page = 'analysis'
            st.rerun()
        
        if st.button("🚨 Emergency Fund", use_container_width=True):
            st.session_state.page = 'emergency'
            st.rerun()
        
        if st.button("📈 Net Worth", use_container_width=True):
            st.session_state.page = 'networth'
            st.rerun()
        
        if st.button("💹 Projections", use_container_width=True):
            st.session_state.page = 'projections'
            st.rerun()
        
        if st.button("🎲 Simulations", use_container_width=True):
            st.session_state.page = 'simulations'
            st.rerun()
        
        if st.button("🎯 Goals", use_container_width=True):
            st.session_state.page = 'goals'
            st.rerun()
        
        if st.button("🤖 AI Chat", use_container_width=True):
            st.session_state.page = 'chat'
            st.rerun()
        
        # Admin section
        if st.session_state.user.get('is_admin'):
            st.markdown("---")
            st.markdown("### 🔐 Admin")
            if st.button("Admin Dashboard", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


def dashboard_page():
    """Display main dashboard."""
    st.markdown('<h1 class="main-header">📊 Financial Dashboard</h1>', unsafe_allow_html=True)
    
    # Get latest financial data
    result, status = api_get('/api/financial-records?limit=1')
    
    if not result.get('success') or not result.get('data'):
        st.info("👋 Welcome! Please submit your financial data to see your dashboard.")
        if st.button("Go to Financial Analysis", use_container_width=True):
            st.session_state.page = 'analysis'
            st.rerun()
        return
    
    record = result['data'][0]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Net Worth",
            f"₹{record['net_worth']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Monthly Savings Rate",
            f"{record['financial_health']['savings_rate']:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Emergency Fund",
            f"{record['emergency_fund']['progress_percentage']:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            "Debt-to-Income",
            f"{record['financial_health']['dti_ratio']:.1f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Financial health status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">🏥 Financial Health</h3>', unsafe_allow_html=True)
        
        # Emergency fund status
        ef_status = record['emergency_fund']['status']
        status_class = f"risk-{ef_status.lower()}"
        
        st.markdown(f"""
        <div class="metric-card">
            <strong>Emergency Fund Status:</strong> <span class="{status_class}">{ef_status}</span><br>
            <strong>Current:</strong> ₹{record['emergency_fund']['current']:,.0f}<br>
            <strong>Target:</strong> ₹{record['emergency_fund']['target']:,.0f}<br>
            <strong>Months Covered:</strong> {record['emergency_fund']['current'] / record['expenses']['monthly_expenses']:.1f} months
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚨 Check Emergency Fund", use_container_width=True):
                st.session_state.page = 'emergency'
                st.rerun()
        with col_b:
            if st.button("📈 View Net Worth", use_container_width=True):
                st.session_state.page = 'networth'
                st.rerun()
    
    with col2:
        st.markdown('<h3 class="sub-header">💼 Asset Allocation</h3>', unsafe_allow_html=True)
        
        # Asset pie chart
        assets = record['assets']
        asset_data = {
            'Category': ['Cash/Savings', 'Investments', 'Real Estate', 'Other'],
            'Amount': [
                assets['cash_savings'],
                assets['investments'],
                assets['real_estate'],
                assets['other']
            ]
        }
        
        fig = px.pie(
            asset_data,
            values='Amount',
            names='Category',
            title='Asset Distribution',
            hole=0.4
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def analysis_page():
    """Display financial analysis page."""
    st.markdown('<h1 class="main-header">💵 Financial Analysis</h1>', unsafe_allow_html=True)
    
    st.markdown("Enter your financial information for a comprehensive analysis.")
    
    with st.form("financial_form"):
        st.markdown("### Income")
        monthly_income = st.number_input("Monthly Income (₹)", min_value=0.0, value=50000.0, step=1000.0)
        
        st.markdown("### Expenses")
        col1, col2 = st.columns(2)
        with col1:
            rent = st.number_input("Rent/Mortgage (₹)", min_value=0.0, value=15000.0, step=500.0)
            utilities = st.number_input("Utilities (₹)", min_value=0.0, value=2000.0, step=100.0)
            groceries = st.number_input("Groceries (₹)", min_value=0.0, value=5000.0, step=500.0)
        with col2:
            transport = st.number_input("Transport (₹)", min_value=0.0, value=3000.0, step=500.0)
            entertainment = st.number_input("Entertainment (₹)", min_value=0.0, value=2000.0, step=500.0)
            other_expenses = st.number_input("Other Expenses (₹)", min_value=0.0, value=3000.0, step=500.0)
        
        total_expenses = rent + utilities + groceries + transport + entertainment + other_expenses
        st.info(f"**Total Monthly Expenses:** ₹{total_expenses:,.2f}")
        
        st.markdown("### Assets")
        col1, col2 = st.columns(2)
        with col1:
            cash_savings = st.number_input("Cash/Savings (₹)", min_value=0.0, value=100000.0, step=10000.0)
            investments = st.number_input("Investments (₹)", min_value=0.0, value=50000.0, step=10000.0)
        with col2:
            real_estate = st.number_input("Real Estate (₹)", min_value=0.0, value=0.0, step=100000.0)
            other_assets = st.number_input("Other Assets (₹)", min_value=0.0, value=0.0, step=10000.0)
        
        st.markdown("### Liabilities")
        col1, col2 = st.columns(2)
        with col1:
            credit_card = st.number_input("Credit Card Debt (₹)", min_value=0.0, value=0.0, step=1000.0)
            student_loans = st.number_input("Student Loans (₹)", min_value=0.0, value=0.0, step=10000.0)
        with col2:
            personal_loans = st.number_input("Personal Loans (₹)", min_value=0.0, value=0.0, step=10000.0)
            mortgage = st.number_input("Mortgage (₹)", min_value=0.0, value=0.0, step=100000.0)
        
        st.markdown("### Emergency Fund")
        emergency_fund = st.number_input("Current Emergency Fund (₹)", min_value=0.0, value=cash_savings * 0.5, step=10000.0)
        
        submitted = st.form_submit_button("Analyze My Finances", use_container_width=True)
    
    if submitted:
        data = {
            'monthly_income': monthly_income,
            'monthly_expenses': total_expenses,
            'rent_expense': rent,
            'utilities_expense': utilities,
            'groceries_expense': groceries,
            'transport_expense': transport,
            'entertainment_expense': entertainment,
            'other_expenses': other_expenses,
            'cash_savings': cash_savings,
            'investments': investments,
            'real_estate': real_estate,
            'other_assets': other_assets,
            'credit_card_debt': credit_card,
            'student_loans': student_loans,
            'personal_loans': personal_loans,
            'mortgage': mortgage,
            'other_liabilities': 0,
            'emergency_fund_amount': emergency_fund
        }
        
        with st.spinner("Analyzing your finances..."):
            result, status = api_post('/api/analyze', data)
        
        if result.get('success'):
            st.success("Analysis complete!")
            
            analysis = result['data']
            
            # Display summary
            st.markdown("### 📊 Analysis Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Net Worth", f"₹{analysis['financial_summary']['net_worth']:,.0f}")
            with col2:
                st.metric("Savings Rate", f"{analysis['financial_summary']['financial_health']['savings_rate']:.1f}%")
            with col3:
                st.metric("DTI Ratio", f"{analysis['financial_summary']['financial_health']['dti_ratio']:.1f}%")
            
            # AI Recommendations
            if 'ai_analysis' in analysis:
                st.markdown("### 🤖 AI Recommendations")
                st.markdown(analysis['ai_analysis'])
        else:
            st.error(result.get('message', 'Analysis failed'))


def emergency_fund_page():
    """Display emergency fund analyzer page."""
    st.markdown('<h1 class="main-header">🚨 Emergency Fund Analyzer</h1>', unsafe_allow_html=True)
    
    result, status = api_get('/api/emergency-fund')
    
    if not result.get('success'):
        st.info("Please submit your financial data first.")
        return
    
    data = result['data']
    
    # Status indicator
    status_colors = {
        'Critical': '#dc3545',
        'Moderate': '#ffc107',
        'Safe': '#28a745'
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Fund", f"₹{data['current_amount']:,.0f}")
    with col2:
        st.metric("Target (6 months)", f"₹{data['target_amount']:,.0f}")
    with col3:
        st.metric("Progress", f"{data['progress_percentage']:.1f}%")
    
    # Progress bar
    progress = min(data['progress_percentage'] / 100, 1.0)
    st.progress(progress)
    
    # Status
    st.markdown(f"""
    <div style="text-align: center; font-size: 1.5rem; margin: 1rem 0;">
        Status: <span style="color: {status_colors.get(data['status'], '#333')}; font-weight: bold;">
            {data['status'].upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendation
    st.markdown("### 💡 Recommendation")
    st.info(data['recommendation'])
    
    # Priority actions
    st.markdown("### ✅ Priority Actions")
    for action in data['priority_actions']:
        st.checkbox(action, key=f"action_{action[:20]}")


def net_worth_page():
    """Display net worth tracking page."""
    st.markdown('<h1 class="main-header">📈 Net Worth Tracker</h1>', unsafe_allow_html=True)
    
    result, status = api_get('/api/net-worth')
    
    if not result.get('success'):
        st.info("Please submit your financial data first.")
        return
    
    data = result['data']
    
    # Current net worth
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Net Worth", f"₹{data['current_net_worth']:,.0f}")
    with col2:
        st.metric("Total Assets", f"₹{data['total_assets']:,.0f}")
    with col3:
        st.metric("Total Liabilities", f"₹{data['total_liabilities']:,.0f}")
    
    # Asset breakdown
    st.markdown("### 💼 Asset Breakdown")
    asset_df = pd.DataFrame([
        {'Category': k.replace('_', ' ').title(), 'Amount': v}
        for k, v in data['asset_breakdown'].items() if v > 0
    ])
    
    if not asset_df.empty:
        fig = px.bar(asset_df, x='Category', y='Amount', title='Assets by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    # Liability breakdown
    st.markdown("### 💳 Liability Breakdown")
    liability_df = pd.DataFrame([
        {'Category': k.replace('_', ' ').title(), 'Amount': v}
        for k, v in data['liability_breakdown'].items() if v > 0
    ])
    
    if not liability_df.empty:
        fig = px.bar(liability_df, x='Category', y='Amount', title='Liabilities by Category', color_discrete_sequence=['#ff6b6b'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical trend
    if data['historical_data']:
        st.markdown("### 📊 Net Worth Trend")
        trend_df = pd.DataFrame(data['historical_data'])
        trend_df['date'] = pd.to_datetime(trend_df['date'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['net_worth'],
            mode='lines+markers',
            name='Net Worth',
            line=dict(color='#2ecc71', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['total_assets'],
            mode='lines',
            name='Assets',
            line=dict(color='#3498db', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['total_liabilities'],
            mode='lines',
            name='Liabilities',
            line=dict(color='#e74c3c', width=2)
        ))
        fig.update_layout(title='Net Worth Over Time', xaxis_title='Date', yaxis_title='Amount (₹)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for rec in data['recommendations']:
        st.info(rec)


def projections_page():
    """Display compound investment projections page."""
    st.markdown('<h1 class="main-header">💹 Investment Projections</h1>', unsafe_allow_html=True)
    
    with st.form("projection_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            principal = st.number_input("Initial Investment (₹)", min_value=0.0, value=100000.0, step=10000.0)
            monthly_contribution = st.number_input("Monthly Contribution (₹)", min_value=0.0, value=5000.0, step=1000.0)
        
        with col2:
            years = st.slider("Investment Period (Years)", min_value=1, max_value=30, value=10)
        
        submitted = st.form_submit_button("Calculate Projections", use_container_width=True)
    
    if submitted:
        data = {
            'principal': principal,
            'monthly_contribution': monthly_contribution,
            'years': years
        }
        
        with st.spinner("Calculating projections..."):
            result, status = api_post('/api/projection', data)
        
        if result.get('success'):
            scenarios = result['data']['scenarios']
            
            # Summary table
            st.markdown("### 📊 Scenario Comparison")
            
            summary_data = []
            for s in scenarios:
                summary_data.append({
                    'Scenario': s['name'],
                    'Final Value': f"₹{s['final_value']:,.0f}",
                    'Total Invested': f"₹{s['total_contributions']:,.0f}",
                    'Interest Earned': f"₹{s['interest_earned']:,.0f}",
                    'Return Multiple': f"{s['final_value']/s['total_contributions']:.2f}x"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
            
            # Growth chart
            st.markdown("### 📈 Growth Comparison")
            
            fig = go.Figure()
            colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
            
            for i, scenario in enumerate(scenarios):
                yearly = scenario['yearly_breakdown']
                years_list = [y['year'] for y in yearly]
                values = [y['value'] for y in yearly]
                
                fig.add_trace(go.Scatter(
                    x=years_list,
                    y=values,
                    mode='lines',
                    name=scenario['name'],
                    line=dict(color=colors[i], width=3)
                ))
            
            fig.update_layout(
                title='Investment Growth Scenarios',
                xaxis_title='Years',
                yaxis_title='Portfolio Value (₹)',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed breakdown for selected scenario
            st.markdown("### 📋 Detailed Breakdown")
            selected = st.selectbox("Select scenario for details", [s['name'] for s in scenarios])
            
            for scenario in scenarios:
                if scenario['name'] == selected:
                    yearly_df = pd.DataFrame(scenario['yearly_breakdown'])
                    st.dataframe(yearly_df, use_container_width=True)
                    break
        else:
            st.error(result.get('message', 'Calculation failed'))


def simulations_page():
    """Display risk simulation page."""
    st.markdown('<h1 class="main-header">🎲 Risk Simulation Engine</h1>', unsafe_allow_html=True)
    
    # Get available scenarios
    scenarios_result, _ = api_get('/api/simulations')
    available_scenarios = scenarios_result.get('data', {}) if scenarios_result.get('success') else {}
    
    tab1, tab2 = st.tabs(["Predefined Scenarios", "Custom Simulation"])
    
    with tab1:
        st.markdown("### Select a Scenario")
        
        scenario_options = {k: f"{v['name']} - {v['description']}" for k, v in available_scenarios.items()}
        selected_scenario = st.selectbox("Choose scenario", options=list(scenario_options.keys()), format_func=lambda x: scenario_options[x])
        
        if st.button("Run Simulation", key="run_predefined"):
            with st.spinner("Running simulation..."):
                result, status = api_post('/api/simulate', {'scenario': selected_scenario})
            
            if result.get('success'):
                display_simulation_results(result['data'])
            else:
                st.error(result.get('message', 'Simulation failed'))
    
    with tab2:
        st.markdown("### Create Custom Scenario")
        
        with st.form("custom_simulation"):
            custom_name = st.text_input("Scenario Name", value="My Custom Scenario")
            income_change = st.slider("Income Change (%)", min_value=-100, max_value=100, value=-20)
            expense_change = st.slider("Expense Change (%)", min_value=-50, max_value=100, value=20)
            interest_change = st.slider("Interest Rate Change (pp)", min_value=-5, max_value=10, value=2)
            
            submitted = st.form_submit_button("Run Custom Simulation")
        
        if submitted:
            data = {
                'custom_name': custom_name,
                'income_change': income_change,
                'expense_change': expense_change,
                'interest_rate_change': interest_change
            }
            
            with st.spinner("Running simulation..."):
                result, status = api_post('/api/simulate', data)
            
            if result.get('success'):
                display_simulation_results(result['data'])
            else:
                st.error(result.get('message', 'Simulation failed'))


def display_simulation_results(data):
    """Display simulation results."""
    scenario = data['scenario']
    metrics = data['metrics']
    
    st.markdown(f"### 📊 Results: {scenario['name']}")
    st.markdown(f"*{scenario['description']}*")
    
    # Risk level badge
    risk_colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
    risk_color = risk_colors.get(data['risk_level'], '#6c757d')
    
    st.markdown(f"""
    <div style="background-color: {risk_color}; color: white; padding: 0.5rem 1rem; 
                border-radius: 5px; display: inline-block; font-weight: bold;">
        Risk Level: {data['risk_level']}
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Savings Rate")
        st.metric(
            "Original",
            f"{metrics['original_savings_rate']:.1f}%",
            delta=f"{metrics['simulated_savings_rate'] - metrics['original_savings_rate']:.1f}%"
        )
        st.metric("Simulated", f"{metrics['simulated_savings_rate']:.1f}%")
    
    with col2:
        st.markdown("#### Debt-to-Income")
        st.metric(
            "Original",
            f"{metrics['original_dti']:.1f}%",
            delta=f"{metrics['simulated_dti'] - metrics['original_dti']:.1f}%"
        )
        st.metric("Simulated", f"{metrics['simulated_dti']:.1f}%")
    
    # Timeline impact
    st.markdown("### ⏱️ Goal Timeline Impact")
    st.info(data['impact_on_timeline'])
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for rec in data['recommendations']:
        st.warning(rec)


def goals_page():
    """Display goals management page."""
    st.markdown('<h1 class="main-header">🎯 Financial Goals</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["My Goals", "Create New Goal"])
    
    with tab1:
        result, status = api_get('/api/goals')
        
        if result.get('success'):
            goals = result.get('data', [])
            
            if not goals:
                st.info("You haven't created any goals yet. Create your first goal!")
            else:
                for goal in goals:
                    with st.expander(f"{'✅' if goal['status'] == 'completed' else '🎯'} {goal['name']} - {goal['progress_percentage']:.1f}%"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Target:** ₹{goal['target_amount']:,.0f}")
                            st.markdown(f"**Current:** ₹{goal['current_amount']:,.0f}")
                            st.markdown(f"**Remaining:** ₹{goal['remaining_amount']:,.0f}")
                        
                        with col2:
                            st.markdown(f"**Type:** {goal['goal_type']}")
                            st.markdown(f"**Priority:** {goal['priority']}")
                            st.markdown(f"**Status:** {goal['status']}")
                        
                        # Progress bar
                        st.progress(min(goal['progress_percentage'] / 100, 1.0))
                        
                        # Actions
                        if goal['status'] != 'completed':
                            contrib_amount = st.number_input(
                                f"Add contribution (₹)",
                                min_value=0.0,
                                key=f"contrib_{goal['id']}"
                            )
                            if st.button("Add Contribution", key=f"btn_contrib_{goal['id']}"):
                                result, _ = api_post(f'/api/goals/{goal["id"]}/contribute', {'amount': contrib_amount})
                                if result.get('success'):
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result.get('message'))
        else:
            st.error("Failed to load goals")
    
    with tab2:
        with st.form("create_goal"):
            name = st.text_input("Goal Name")
            description = st.text_area("Description (optional)")
            target_amount = st.number_input("Target Amount (₹)", min_value=1000.0, step=1000.0)
            current_amount = st.number_input("Current Amount (₹)", min_value=0.0, step=1000.0)
            monthly_contribution = st.number_input("Monthly Contribution (₹)", min_value=0.0, step=500.0)
            
            col1, col2 = st.columns(2)
            with col1:
                goal_type = st.selectbox("Goal Type", ['savings', 'investment', 'debt_repayment', 'purchase'])
            with col2:
                priority = st.selectbox("Priority", ['low', 'medium', 'high'])
            
            submitted = st.form_submit_button("Create Goal", use_container_width=True)
        
        if submitted:
            data = {
                'name': name,
                'description': description,
                'target_amount': target_amount,
                'current_amount': current_amount,
                'monthly_contribution': monthly_contribution,
                'goal_type': goal_type,
                'priority': priority
            }
            
            result, status = api_post('/api/goals', data)
            
            if result.get('success'):
                st.success("Goal created successfully!")
                st.rerun()
            else:
                st.error(result.get('message', 'Failed to create goal'))


def chat_page():
    """Display AI chat page."""
    st.markdown('<h1 class="main-header">🤖 AI Financial Assistant</h1>', unsafe_allow_html=True)
    
    # Suggested questions
    result, _ = api_get('/api/chat/suggestions')
    suggestions = result.get('suggestions', []) if result.get('success') else []
    
    if suggestions:
        st.markdown("### 💡 Suggested Questions")
        cols = st.columns(min(len(suggestions), 3))
        for i, suggestion in enumerate(suggestions[:3]):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    st.session_state.current_question = suggestion
                    st.rerun()
    
    # Chat interface
    st.markdown("### 💬 Ask me anything about your finances")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
    
    # Input
    question = st.chat_input("Type your question here...")
    
    # Use suggested question if set
    if 'current_question' in st.session_state:
        question = st.session_state.current_question
        del st.session_state.current_question
    
    if question:
        # Add user message
        st.session_state.chat_history.append({'role': 'user', 'content': question})
        
        with st.chat_message('user'):
            st.markdown(question)
        
        # Get AI response
        with st.chat_message('assistant'):
            with st.spinner("Thinking..."):
                result, status = api_post('/api/chat', {'question': question})
            
            if result.get('success'):
                answer = result['answer']
                st.markdown(answer)
                st.session_state.chat_history.append({'role': 'assistant', 'content': answer})
            else:
                error_msg = result.get('message', 'Sorry, I encountered an error.')
                st.error(error_msg)
    
    # Clear history button
    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            api_post('/api/chat/clear')
            st.session_state.chat_history = []
            st.rerun()


def admin_page():
    """Display admin dashboard page."""
    st.markdown('<h1 class="main-header">🔐 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    result, status = api_get('/admin/dashboard')
    
    if not result.get('success'):
        st.error("Access denied or error loading admin data")
        return
    
    data = result.get('data', {})
    overview = data.get('overview', {})
    risk_summary = data.get('risk_summary', {})
    
    # Overview metrics
    st.markdown("### 📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", overview.get('users', {}).get('total', 0))
    with col2:
        st.metric("Active (30d)", overview.get('users', {}).get('active_30d', 0))
    with col3:
        st.metric("New (7d)", overview.get('users', {}).get('new_7d', 0))
    with col4:
        goals = overview.get('goals', {})
        st.metric("Goals Completed", f"{goals.get('completed', 0)}/{goals.get('total', 0)}")
    
    # Risk distribution
    st.markdown("### 🎯 Risk Distribution")
    
    risk_data = risk_summary.get('risk_distribution', {})
    risk_df = pd.DataFrame([
        {'Level': k.title(), 'Count': v}
        for k, v in risk_data.items() if k != 'total' and k != 'percentages'
    ])
    
    if not risk_df.empty:
        fig = px.pie(
            risk_df,
            values='Count',
            names='Level',
            title='User Risk Distribution',
            color='Level',
            color_discrete_map={
                'Critical': '#dc3545',
                'High': '#fd7e14',
                'Medium': '#ffc107',
                'Low': '#28a745'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Financial health
    st.markdown("### 💰 Average Financial Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Avg Savings Rate", f"{overview.get('financial_health', {}).get('average_savings_rate', 0):.1f}%")
    with col2:
        st.metric("Avg DTI", f"{overview.get('financial_health', {}).get('average_dti', 0):.1f}%")
    
    # Recent users
    st.markdown("### 👥 Recent Users")
    recent_users = data.get('recent_users', {}).get('users', [])
    
    if recent_users:
        users_df = pd.DataFrame([
            {
                'Username': u['username'],
                'Email': u['email'],
                'Admin': 'Yes' if u['is_admin'] else 'No',
                'Created': u['created_at'][:10] if u['created_at'] else ''
            }
            for u in recent_users
        ])
        st.dataframe(users_df, use_container_width=True)


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    if not is_authenticated():
        login_page()
    else:
        sidebar()
        
        page = st.session_state.page
        
        if page == 'dashboard':
            dashboard_page()
        elif page == 'analysis':
            analysis_page()
        elif page == 'emergency':
            emergency_fund_page()
        elif page == 'networth':
            net_worth_page()
        elif page == 'projections':
            projections_page()
        elif page == 'simulations':
            simulations_page()
        elif page == 'goals':
            goals_page()
        elif page == 'chat':
            chat_page()
        elif page == 'admin' and st.session_state.user.get('is_admin'):
            admin_page()
        else:
            dashboard_page()


if __name__ == '__main__':
    main()
