from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import json
from datetime import datetime, timedelta
import yfinance as yf
from flask import Response
import time
import random  # For demo data

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(20), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'stock_symbol': self.stock_symbol,
            'stock_name': self.stock_name,
            'date_added': self.date_added.strftime('%Y-%m-%d %H:%M:%S')
        }

User.wishlist = db.relationship('Wishlist', backref='user', lazy=True)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/search_stocks')
@login_required
def search_stocks():
    query = request.args.get('query', '').lower()
    if not query or len(query) < 2:
        return jsonify([])
    
    # Read the stock names from CSV
    df = pd.read_csv('data/stock_names.csv')
    
    # Filter stocks based on query
    filtered_stocks = df[
        (df['tag'].str.lower().str.contains(query)) |
        (df['name'].str.lower().str.contains(query))
    ].head(10)
    
    # Format results
    results = [{'symbol': row['tag'], 'name': row['name']} 
              for _, row in filtered_stocks.iterrows()]
    
    return jsonify(results)

# Cache for storing stock data
stock_cache = {}
CACHE_DURATION = 60  # 60 seconds (1 minute)

@app.route('/get_stock_data')
@login_required
def get_stock_data():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify([])
    
    try:
        stock = yf.Ticker(symbol)
        # Get intraday data for today
        df = stock.history(period="1d", interval="1m")
        
        # Format data for TradingView chart
        data = []
        for index, row in df.iterrows():
            data.append({
                'time': index.strftime('%Y-%m-%d %H:%M'),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return jsonify([])

@app.route('/get_latest_price')
@login_required
def get_latest_price():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'No symbol provided'})
    
    try:
        stock = yf.Ticker(symbol)
        current_data = stock.history(period="1d", interval="1m").iloc[-1]
        
        return jsonify({
            'price': round(float(current_data['Close']), 2),
            'change': round(float(current_data['Close'] - current_data['Open']), 2),
            'changePercent': round(float((current_data['Close'] - current_data['Open']) / current_data['Open'] * 100), 2),
            'volume': int(current_data['Volume']),
            'time': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        print(f"Error fetching latest price for {symbol}: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/get_latest_candle')
@login_required
def get_latest_candle():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'No symbol provided'})
    
    try:
        stock = yf.Ticker(symbol)
        # Get the latest minute's data
        df = stock.history(period="1d", interval="1m").tail(1)
        
        if len(df) > 0:
            latest = df.iloc[-1]
            # Format timestamp for intraday data
            timestamp = latest.name.strftime('%Y-%m-%d %H:%M')
            data = {
                'time': timestamp,
                'open': round(float(latest['Open']), 2),
                'high': round(float(latest['High']), 2),
                'low': round(float(latest['Low']), 2),
                'close': round(float(latest['Close']), 2),
                'volume': int(latest['Volume'])
            }
            return jsonify(data)
    except Exception as e:
        print(f"Error fetching latest candle for {symbol}: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.get_json()
    symbol = data.get('symbol')
    name = data.get('name')
    
    if not symbol or not name:
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=current_user.id, stock_symbol=symbol).first()
    if existing:
        return jsonify({'error': 'Stock already in wishlist'}), 400
        
    wishlist_item = Wishlist(
        user_id=current_user.id,
        stock_symbol=symbol,
        stock_name=name
    )
    
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify(wishlist_item.to_dict())

@app.route('/remove_from_wishlist/<int:item_id>', methods=['DELETE'])
@login_required
def remove_from_wishlist(item_id):
    wishlist_item = Wishlist.query.get_or_404(item_id)
    
    if wishlist_item.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.delete(wishlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed successfully'})

@app.route('/get_wishlist')
@login_required
def get_wishlist():
    wishlist = Wishlist.query.filter_by(user_id=current_user.id).all()
    return jsonify([item.to_dict() for item in wishlist])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=False)
