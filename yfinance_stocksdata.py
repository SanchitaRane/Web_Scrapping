import yfinance as yf
import pandas as pd

# Define the stock ticker symbol
ticker_symbol = 'AAPL'  # Replace with the ticker symbol you want

# Define the time period from 2020 to the end of Q1 2024
start_date = '2020-01-01'
end_date = '2024-03-31'

# Download stock data
stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

# Keep only the 'Close' column, which represents the closing price
closing_data = stock_data[['Close']]

# Save the closing data to a CSV file
closing_data.to_csv(f'{ticker_symbol}_closing_data_2020_to_2024Q1.csv', index=True)
print(f"Closing data saved to '{ticker_symbol}_closing_data_2020_to_2024Q1.csv'")