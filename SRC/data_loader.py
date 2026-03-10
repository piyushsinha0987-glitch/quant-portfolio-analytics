import pandas as pd
import yfinance as yf


# ==============================
# Load Portfolio Symbols
# ==============================

def get_portfolio_data():
    """
    Load portfolio holdings from CSV file.
    """

    try:
        portfolio_df = pd.read_csv("../Data/stocks.csv")

    except FileNotFoundError:
        raise FileNotFoundError(
            "stocks.csv not found. Please place it inside the Data folder."
        )

    return portfolio_df


# ==============================
# Download Market Data
# ==============================

def load_market_data(tickers, start="2020-01-01", end="2024-01-01"):

    data = yf.download(
        tickers,
        start=start,
        end=end,
        progress=False
    )

    # Handle both cases: Adj Close or Close
    if "Adj Close" in data.columns:
        prices = data["Adj Close"]
    else:
        prices = data["Close"]

    returns = prices.pct_change().dropna()

    return returns