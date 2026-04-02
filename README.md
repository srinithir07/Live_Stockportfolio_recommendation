# STOCK PULSE

Stock Pulse is an AI-driven live stock portfolio recommendation system. It leverages real-time financial market data and advanced analytics to help users manage their investments effectively. Built with a sleek, premium dark-mode glassmorphism UI, Stock Pulse provides an elegant and insightful dashboard for investors of all levels.

## FEATURES

- Live Market Data: Fetches real-time stock data directly from Yahoo Finance.  
- AI Recommendations: Generates smart investment recommendations based on market trends to fit your budget and risk profile.  
- Technical Analysis: Utilizes powerful quantitative analysis leveraging Pandas and NumPy for tracking moving averages, momentum, and more.  
- Sentiment Analysis: Integrates Natural Language Processing (NLP) with TextBlob to gauge market sentiment dynamically.  
- Dynamic Visualizations: Provides clear and intuitive visual graphs of stock trends using Matplotlib.  
- Portfolio Management: Allows users to track their existing investments, monitor current valuations, and manage their portfolios via an SQLite database.  
- Premium Web UI: Includes a dynamic "sunset gradient" dark-mode glassmorphism interface for a stunning aesthetic user experience.  
- User Authentication: Secure login and registration functionality to keep user portfolios private.  

## TECH STACK

- Backend: Python, Flask, Werkzeug  
- Database: SQLite3  
- Data Science & AI: Pandas, NumPy, yfinance, TextBlob  
- Visualization: Matplotlib  
- Frontend: HTML5, CSS3 (Vanilla CSS with Glassmorphism), Jinja2 Templates  

## PREREQUISITES

Before you begin, make sure you have the following installed on your machine:

- Python 3.8+  
- pip (Python package installer)  

## INSTALLATION AND SETUP

Clone or Download the Repository. Ensure you have the project directory on your local machine.

### Create a Virtual Environment (Recommended)

```bash
python -m venv venv

stock-portfolio/
│
├── app.py                 # Main Flask application logic and routing
├── models.py              # SQLite database schema and initialization
├── utils.py               # Core business logic: yfinance API calls, sentiment & technical analysis
├── requirements.txt       # Python package dependencies
├── investment.db          # Local SQLite Database (created after running models.py)
│
├── static/                # Static assets (Custom CSS, JS, Images, Generated Plots)
│   └── ...
│
└── templates/             # HTML Templates (Jinja2)
    ├── dashboard.html     # User Portfolio Dashboard
    ├── recommend.html     # AI Recommendations Interface
    ├── register.html      # User Registration Page
    ├── add_investment.html# Add New Stock to Portfolio
    ├── edit_investment.html# Edit existing stock
    ├── trends.html        # Interactive Matplotlib charts and graphs
    └── ...

    
