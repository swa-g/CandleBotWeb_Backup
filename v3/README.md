# CandleBotWeb

## Project Overview
CandleBotWeb is a Python Flask web application that provides users with a platform to register, log in, and view stock data. The application features a dashboard that allows users to search for Indian stocks and view real-time price charts using TradingView's Lightweight Charts.

## Features
- **User Authentication**: Users can register and log in securely.
- **Stock Dashboard**: A dedicated page for searching and viewing stock data.
- **Real-Time Data**: Fetches real-time stock prices using the yfinance library.
- **Charting**: Displays stock price movements with candlestick charts.
- **Wishlist Feature**: Users can add stocks to their wishlist for quick access.
- **Responsive Design**: The application is designed to be mobile-friendly.

## Installation Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd CandleBotWeb
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have the stock names data in the `data` directory:
   - `stock_names.csv`
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage
- **Register**: Create a new account using the registration form.
- **Login**: Use your credentials to log in.
- **Dashboard**: Search for stocks by name or symbol in the dashboard.
- **View Charts**: Click on a stock to view its price chart and real-time updates.
- **Wishlist**: Add stocks to your wishlist for easy access.

## Technologies Used
- **Flask**: A lightweight WSGI web application framework.
- **SQLAlchemy**: ORM for database management.
- **yfinance**: Library to fetch real-time stock data from Yahoo Finance.
- **Bootstrap**: For responsive design and styling.
- **TradingView Lightweight Charts**: For displaying stock charts.
