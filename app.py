import os
import sqlite3
import pandas as pd
import yfinance as yf
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from utils import analyze_stock_technical, analyze_stock_sentiment, plot_stock_chart, get_final_recommendation, analyze_and_plot_trends
from models import init_db

# Config app
app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db():
    conn = sqlite3.connect("investment.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password")) 
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?,?)",(username, password))
            conn.commit()
            flash("Account created successfully! Please Login", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    investments = conn.execute("SELECT * FROM investments WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    portfolio = []
    total_cost = 0.0
    total_value = 0.0
    
    for inv in investments:
        symbol = inv["symbol"]
        qty = inv["quantity"]
        buy_price = inv["buy_price"]
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
            else:
                current_price = buy_price
        except Exception:
            current_price = buy_price
            
        current_price = float(current_price)
        value = current_price * qty
        cost = buy_price * qty
        p_l = value - cost
        
        total_cost += cost
        total_value += value
        
        portfolio.append({
            "id": inv["id"],
            "symbol": symbol,
            "category": inv["category"],
            "quantity": qty,
            "buy_price": round(buy_price, 2),
            "current_price": round(current_price, 2),
            "value": round(value, 2),
            "profit_loss": round(p_l, 2)
        })
        
    total_profit_loss = total_value - total_cost
    
    return render_template(
        "dashboard.html",
        investments=portfolio,
        total_value=round(total_value, 2),
        total_cost=round(total_cost, 2),
        profit_loss=round(total_profit_loss, 2)
    )

@app.route("/add", methods=["GET", "POST"])
def add_investment():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol: symbol = symbol.upper()
        category = request.form.get("category")
        quantity = request.form.get("quantity")
        buy_price = request.form.get("buy_price")
        
        if not symbol or not category or not quantity or not buy_price:
            flash("All fields are required.", "danger")
            return redirect(url_for("add_investment"))
            
        quantity = float(quantity)
        buy_price = float(buy_price)
        
        conn = get_db()
        conn.execute("INSERT INTO investments (user_id, symbol, category, quantity, buy_price) VALUES (?,?,?,?,?)", 
                     (session["user_id"], symbol, category, quantity, buy_price))
        conn.commit()
        flash("Investment added successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_investment.html")

@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete_investment(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("DELETE FROM investments WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    conn.commit()
    flash("Investment deleted successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_investment(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol: symbol = symbol.upper()
        category = request.form.get("category")
        quantity = float(request.form.get("quantity"))
        buy_price = float(request.form.get("buy_price"))
        
        conn.execute("UPDATE investments SET symbol = ?, category = ?, quantity = ?, buy_price = ? WHERE id = ? AND user_id = ?", 
                     (symbol, category, quantity, buy_price, id, session["user_id"]))
        conn.commit()
        flash("Investment updated successfully!", "success")
        return redirect(url_for("dashboard"))
        
    investment = conn.execute("SELECT * FROM investments WHERE id = ? AND user_id = ?", (id, session["user_id"])).fetchone()
    if not investment:
        flash("Investment not found.", "danger")
        return redirect(url_for("dashboard"))
        
    return render_template("edit_investment.html", investment=investment)

@app.route("/export")
def export_csv():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    investments = conn.execute("SELECT symbol, category, quantity, buy_price FROM investments WHERE user_id = ?", (session["user_id"],)).fetchall()
    
    csv_data = "Symbol,Category,Quantity,Buy Price\n"
    for inv in investments:
        csv_data += f"{inv['symbol']},{inv['category']},{inv['quantity']},{inv['buy_price']}\n"
        
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=portfolio.csv"}
    )

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    result = None
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol: symbol = symbol.upper()
        api_key = request.form.get("api_key")
        
        if not symbol:
            flash("Please enter a stock symbol.", "danger")
            return redirect(url_for("recommend"))
            
        # 1. Technical Analysis
        tech_data, tech_err = analyze_stock_technical(symbol)
        if tech_err or not tech_data:
            flash(f"Error analyzing technical data: {tech_err}", "danger")
            return redirect(url_for("recommend"))
            
        # 2. NLP Sentiment Analysis
        sentiment_score, sent_err = analyze_stock_sentiment(symbol, api_key)
        
        # 3. Visualization
        plot_url = plot_stock_chart(symbol, tech_data["hist_data"])
        
        # 4. Final Verdict
        verdict = get_final_recommendation(tech_data["signal"], sentiment_score)
        
        result = {
            "symbol": symbol,
            "current_price": tech_data["current_price"],
            "sma_50": tech_data["sma_50"],
            "sma_200": tech_data["sma_200"],
            "tech_signal": tech_data["signal"],
            "sentiment_score": round(sentiment_score, 2),
            "sentiment_error": sent_err,
            "plot_url": plot_url,
            "verdict": verdict
        }
        
    return render_template("recommend.html", result=result)

@app.route("/trends/<symbol>")
def view_trends(symbol):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    analysis_data, error = analyze_and_plot_trends(symbol)
    if error or not analysis_data:
        flash(f"Error executing Pandas trend analysis for {symbol}: {error}", "danger")
        return redirect(url_for("dashboard"))
        
    return render_template("trends.html", symbol=symbol, analysis=analysis_data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
