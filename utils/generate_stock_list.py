import pandas as pd

stock_data = [
        {'name': 'Apple Inc.', 'tag': 'AAPL', 'market': 'NASDAQ'},
        {'name': 'Microsoft Corporation', 'tag': 'MSFT', 'market': 'NASDAQ'},
        {'name': 'Tesla, Inc.', 'tag': 'TSLA', 'market': 'NASDAQ'},
        # Add more stock data as needed
    ]
    
    # Format the suggestions

# Save to pickle
pd.DataFrame(stock_data).to_pickle('data/stock_names.pkl')