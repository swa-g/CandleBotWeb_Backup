import pandas as pd

# Read stock data from the CSV file
stock_names_csv_path = 'data/stock_names.csv'  # Adjust the path as necessary
stock_df = pd.read_csv(stock_names_csv_path)

# Ensure the DataFrame contains the necessary columns
if 'name' in stock_df.columns and 'tag' in stock_df.columns and 'market' in stock_df.columns:
    # Convert the DataFrame to a list of dictionaries
    stock_data = stock_df.to_dict(orient='records')

    # Save to pickle
    pd.DataFrame(stock_data).to_pickle('data/stock_names.pkl')
else:
    print("CSV file must contain 'name', 'tag', and 'market' columns.")