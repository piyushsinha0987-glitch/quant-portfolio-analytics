import pandas as pd


def get_portfolio_data():

    """
    Load portfolio holdings from CSV file
    """

    try:
        portfolio_df = pd.read_csv("../Data/stocks.csv")

    except FileNotFoundError:
        raise FileNotFoundError(
            "stocks.csv not found. Please place it inside the Data folder."
        )

    return portfolio_df