import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Needed to run matplotlib in the background without a GUI
import matplotlib.pyplot as plt
import requests
from textblob import TextBlob

# 1. Technical Analysis (NumPy & Pandas)
def analyze_stock_technical(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        if hist.empty:
            return None, "No historical data found for symbol."

        # Calculate Moving Averages using pandas and numpy
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        
        current_price = hist['Close'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        sma_200 = hist['SMA_200'].iloc[-1]

        signal = "Neutral"
        if not pd.isna(sma_50) and not pd.isna(sma_200):
            if sma_50 > sma_200:
                signal = "Bullish (Golden Cross)"
            elif sma_50 < sma_200:
                signal = "Bearish (Death Cross)"
        
        technical_data = {
            "current_price": round(current_price, 2),
            "sma_50": round(sma_50, 2) if not pd.isna(sma_50) else None,
            "sma_200": round(sma_200, 2) if not pd.isna(sma_200) else None,
            "signal": signal,
            "hist_data": hist
        }
        return technical_data, None
    except Exception as e:
        return None, str(e)

# 2. Sentiment Analysis (NLP & TextBlob)
def analyze_stock_sentiment(symbol, api_key=None):
    if not api_key:
        return 0.0, "No API key provided. Skipping NLP..."
        
    url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") != "ok":
            return 0.0, data.get("message", "Error fetching news.")
            
        articles = data.get("articles", [])[:10]
        if not articles:
            return 0.0, "No recent news found."
            
        total_polarity = 0.0
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            blob = TextBlob(text)
            total_polarity += blob.sentiment.polarity
            
        avg_polarity = total_polarity / len(articles)
        return avg_polarity, None
    except Exception as e:
        return 0.0, str(e)

# 3. Graphical Visualization (Matplotlib)
def plot_stock_chart(symbol, hist):
    try:
        # Ensure static/plots directory exists
        plot_dir = os.path.join(os.path.dirname(__file__), "static", "plots")
        os.makedirs(plot_dir, exist_ok=True)
        
        filepath = os.path.join(plot_dir, f"{symbol}_chart.png")
        
        plt.figure(figsize=(10, 5), facecolor='#0d1117')
        ax = plt.axes()
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#8b949e')
        
        plt.plot(hist.index, hist['Close'], label='Close Price', color='#58a6ff')
        if 'SMA_50' in hist.columns:
            plt.plot(hist.index, hist['SMA_50'], label='50-Day SMA', color='#A371F7')
        if 'SMA_200' in hist.columns:
            plt.plot(hist.index, hist['SMA_200'], label='200-Day SMA', color='#2ea043')
            
        plt.title(f"{symbol} 1-Year Price & Moving Averages", color='#e6edf3')
        plt.xlabel('Date', color='#8b949e')
        plt.ylabel('Price', color='#8b949e')
        plt.xticks(rotation=45)
        
        legend = plt.legend()
        plt.setp(legend.get_texts(), color='#e6edf3')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=100)
        plt.close()
        
        return f"/static/plots/{symbol}_chart.png"
    except Exception as e:
        print("Plot error:", e)
        return None

# 4. Final Scoring Output
def get_final_recommendation(tech_signal, sentiment_score):
    if "Bullish" in tech_signal:
        if sentiment_score > 0.3:
            return "STRONG BUY"
        elif sentiment_score >= 0.0:
            return "BUY"
        else:
            return "HOLD"
    elif "Bearish" in tech_signal:
        if sentiment_score < -0.3:
            return "STRONG SELL"
        elif sentiment_score < 0.0:
            return "SELL"
        else:
            return "HOLD"
    else:
        # Neutral technical
        if sentiment_score > 0.4: return "BUY"
        if sentiment_score < -0.4: return "SELL"
        return "HOLD"

# 5. Advanced Trend Analysis (Pandas & Matplotlib)
def analyze_and_plot_trends(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        if hist.empty:
            return None, "No historical data found for symbol."

        # Advanced Pandas Data Analysis
        # 1. Moving Averages
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        # 2. Bollinger Bands (Volatility)
        hist['BB_std'] = hist['Close'].rolling(window=20).std()
        hist['BB_upper'] = hist['SMA_20'] + (hist['BB_std'] * 2)
        hist['BB_lower'] = hist['SMA_20'] - (hist['BB_std'] * 2)
        
        # 3. Trend Patterns
        current_price = hist['Close'].iloc[-1]
        upper_band = hist['BB_upper'].iloc[-1]
        lower_band = hist['BB_lower'].iloc[-1]
        
        pattern = "Consolidating (Within Bands)"
        if not pd.isna(upper_band) and current_price > upper_band:
            pattern = "Overbought (Above Upper Bollinger Band)"
        elif not pd.isna(lower_band) and current_price < lower_band:
            pattern = "Oversold (Below Lower Bollinger Band)"

        # Matplotlib Plotting
        plot_dir = os.path.join(os.path.dirname(__file__), "static", "plots")
        os.makedirs(plot_dir, exist_ok=True)
        filepath = os.path.join(plot_dir, f"{symbol}_trends.png")
        
        plt.figure(figsize=(12, 6), facecolor='#0d1117')
        ax = plt.axes()
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#8b949e')
            
        plt.plot(hist.index, hist['Close'], label='Close Price', color='#58a6ff')
        if 'SMA_20' in hist.columns:
            plt.plot(hist.index, hist['SMA_20'], label='20-Day SMA', color='#A371F7', linestyle='--')
        if 'BB_upper' in hist.columns and 'BB_lower' in hist.columns:
            plt.fill_between(hist.index, hist['BB_lower'], hist['BB_upper'], color='#A371F7', alpha=0.1, label='Bollinger Bands (Pandas Volatility)')
            
        plt.title(f"{symbol} Pandas Trend Analysis & Bollinger Bands", color='#e6edf3')
        plt.xlabel('Date', color='#8b949e')
        plt.ylabel('Price', color='#8b949e')
        plt.xticks(rotation=45)
        
        legend = plt.legend()
        plt.setp(legend.get_texts(), color='#e6edf3')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=100)
        plt.close()
        
        analysis_data = {
            "current_price": round(current_price, 2),
            "sma_20": round(hist['SMA_20'].iloc[-1], 2) if not pd.isna(hist['SMA_20'].iloc[-1]) else None,
            "pattern": pattern,
            "plot_url": f"/static/plots/{symbol}_trends.png"
        }
        return analysis_data, None
    except Exception as e:
        print("Pandas/Matplotlib error:", e)
        return None, str(e)
