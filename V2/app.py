from flask import Flask, jsonify, render_template, redirect, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import pandas as pd
import os
import yfinance as yf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

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
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        pickle_file_path = os.path.join('data', 'users.pkl')
        if os.path.exists(pickle_file_path):
            users_df = pd.read_pickle(pickle_file_path)
        else:
            users_df = pd.DataFrame(columns=['full_name', 'username', 'email', 'password', 'portfolio', 'watchlist'])

        if form.username.data in users_df['username'].values:
            flash('Username already exists. Please choose a different one.')
            return redirect('/register')

        new_user = pd.DataFrame({
            'full_name': [form.full_name.data],
            'username': [form.username.data],
            'email': [form.email.data],
            'password': [form.password.data],  # Consider hashing the password before storing
            'portfolio': [''],
            'watchlist': ['']
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


if __name__ =="__main__":
    app.run(debug=True)