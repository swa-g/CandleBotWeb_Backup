from flask import Flask, jsonify, render_template, redirect, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import pandas as pd
import os
import yfinance as yf
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key

# Define the registration and login forms
class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        pickle_file_path = os.path.join('data', 'users.pkl')

        if os.path.exists(pickle_file_path):
            users_df = pd.read_pickle(pickle_file_path)
        else:
            users_df = pd.DataFrame(columns=['full_name', 'username', 'email', 'password'])

        if form.username.data in users_df['username'].values:
            flash('Username already exists. Please choose a different one.')
            return redirect('/register')

        new_user = pd.DataFrame({
            'full_name': [form.full_name.data],
            'username': [form.username.data],
            'email': [form.email.data],
            'password': [form.password.data]  # Consider hashing the password before storing
        })

        # Use pd.concat instead of append
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_pickle(pickle_file_path)
        flash('Registration successful! You can now log in.')
        return redirect('/login')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pickle_file_path = os.path.join('data', 'users.pkl')

        if os.path.exists(pickle_file_path):
            users_df = pd.read_pickle(pickle_file_path)

            user = users_df[(users_df['username'] == form.username.data) & (users_df['password'] == form.password.data)]
            if not user.empty:
                session['full_name'] = user['full_name'].values[0]  # Store the full name in the session
                flash('Login successful!')
                return redirect('/dashboard')  # Redirect to the dashboard on successful login
            else:
                flash('Invalid username or password. Please try again.')

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    full_name = session.get('full_name')  # Retrieve the full name from the session
    if full_name:
        return render_template('dashboard.html', full_name=full_name)
    else:
        return redirect('/login')  # Redirect to login if not logged in

@app.route('/logout')
def logout():
    session.pop('full_name', None)  # Remove the full name from the session
    flash('You have been logged out.')
    return redirect('/')  # Redirect to home after logout

@app.route('/fetch_stock_data', methods=['GET'])
def fetch_stock_data():
    stock_symbol = request.args.get('symbol')
    period = request.args.get('period')
    interval = request.args.get('interval')
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    # Fetch the data using yfinance
    
    if period == "None":
        df = yf.download(stock_symbol, interval=interval, start=start_date, end=end_date, multi_level_index=False, progress=False) 
    else:
        df = yf.download(stock_symbol, period=period, interval=interval, multi_level_index=False, progress=False)
        
    # Prepare the data for the chart
    data = []
    for index, row in df.iterrows():
        data.append({
            'time': index.strftime('%Y-%m-%d'),
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close']
        })

    return jsonify(data)

if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)