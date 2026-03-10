import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

from data_loader import get_portfolio_data, load_market_data
from optimizers import min_variance_weights, risk_parity_weights, max_drawdown
from monte_carlo import simulate_joint_returns


# ==============================
# Portfolio Evaluation Function
# ==============================

def evaluate_portfolio(weights, returns_df):

    portfolio_returns = returns_df @ weights

    expected_return = np.mean(portfolio_returns) * 252
    volatility = np.std(portfolio_returns) * np.sqrt(252)

    sharpe_ratio = 0 if volatility == 0 else expected_return / volatility

    return expected_return, volatility, sharpe_ratio


# ==============================
# Main Program
# ==============================

def main():

    np.random.seed(42)

    # ==============================
    # Load & Clean Data
    # ==============================

    stocks_df = pd.read_csv("../Data/stocks.csv")
    portfolio_df = get_portfolio_data()

    stocks_df["Symbol"] = stocks_df["Symbol"].str.upper().str.strip()
    portfolio_df["Symbol"] = portfolio_df["Symbol"].str.upper().str.strip()

    merged_df = pd.merge(portfolio_df, stocks_df, on="Symbol")

    # Extract tickers
    symbols = merged_df["Symbol"].tolist()

    # Download market data
    returns_df = load_market_data(symbols)

    # ==============================
    # Monte Carlo Simulation
    # ==============================

    n_sim = 100

    mv_sharpes = []
    rp_sharpes = []
    equal_sharpes = []

    for _ in range(n_sim):

        returns_df = simulate_joint_returns(symbols)
        n_assets = returns_df.shape[1]

        equal_weights = np.ones(n_assets) / n_assets
        mv_weights = min_variance_weights(returns_df)
        rp_weights = risk_parity_weights(returns_df)

        mv_sharpes.append(evaluate_portfolio(mv_weights, returns_df)[2])
        rp_sharpes.append(evaluate_portfolio(rp_weights, returns_df)[2])
        equal_sharpes.append(evaluate_portfolio(equal_weights, returns_df)[2])

    # ==============================
    # Sharpe Ratio Distribution
    # ==============================

    plt.figure(figsize=(10,6))

    plt.hist(mv_sharpes, bins=30, alpha=0.5, label="Minimum Variance")
    plt.hist(rp_sharpes, bins=30, alpha=0.5, label="Risk Parity")
    plt.hist(equal_sharpes, bins=30, alpha=0.5, label="Equal Weight")

    plt.title("Sharpe Ratio Distribution Across Simulations")
    plt.xlabel("Sharpe Ratio")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)

    plt.legend()
    plt.show()

    # ==============================
    # Efficient Frontier
    # ==============================

    num_portfolios = 5000
    risk_free_rate = 0.02

    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()

    n_assets = len(returns_df.columns)

    results = np.zeros((num_portfolios, 3))
    weights_record = []

    for i in range(num_portfolios):

        weights = np.random.dirichlet(np.ones(n_assets))

        portfolio_return = np.sum(mean_returns * weights) * 252

        portfolio_volatility = np.sqrt(
            weights.T @ (cov_matrix * 252) @ weights
        )

        sharpe = 0 if portfolio_volatility == 0 else (
            portfolio_return - risk_free_rate
        ) / portfolio_volatility

        results[i] = [portfolio_return, portfolio_volatility, sharpe]
        weights_record.append(weights)

    results_array = np.array(results)

    # ==============================
    # Best Portfolios
    # ==============================

    max_sharpe_idx = np.argmax(results_array[:,2])
    min_vol_idx = np.argmin(results_array[:,1])

    max_sharpe_vol = results_array[max_sharpe_idx,1]
    max_sharpe_ret = results_array[max_sharpe_idx,0]

    min_vol_vol = results_array[min_vol_idx,1]
    min_vol_ret = results_array[min_vol_idx,0]

    # ==============================
    # Portfolio Risk Statistics
    # ==============================

    best_weights = weights_record[max_sharpe_idx]

    portfolio_returns = returns_df @ best_weights
    cum_returns = (1 + portfolio_returns).cumprod()

    expected_return = np.mean(portfolio_returns) * 252
    volatility = np.std(portfolio_returns) * np.sqrt(252)

    sharpe_ratio = 0 if volatility == 0 else (
        expected_return - risk_free_rate
    ) / volatility

    var_95 = np.percentile(portfolio_returns, 5)
    cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()

    mdd = max_drawdown(cum_returns)
    calmar_ratio = expected_return / abs(mdd) if mdd != 0 else 0

    print("\nPortfolio Risk Statistics")
    print("-------------------------")
    print(f"Expected Return: {expected_return:.2%}")
    print(f"Volatility: {volatility:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"VaR (95%): {var_95:.2%}")
    print(f"CVaR (95%): {cvar_95:.2%}")
    print(f"Max Drawdown: {mdd:.2%}")
    print(f"Calmar Ratio: {calmar_ratio:.2f}")

    # ==============================
    # Efficient Frontier Plot
    # ==============================

    plt.figure(figsize=(10,6))

    scatter = plt.scatter(
        results_array[:,1],
        results_array[:,0],
        c=results_array[:,2],
        cmap="viridis",
        alpha=0.4
    )

    plt.colorbar(scatter, label="Sharpe Ratio")

    plt.scatter(
        max_sharpe_vol,
        max_sharpe_ret,
        color="red",
        marker="*",
        s=300,
        label="Max Sharpe"
    )

    plt.scatter(
        min_vol_vol,
        min_vol_ret,
        color="blue",
        marker="*",
        s=300,
        label="Min Volatility"
    )

    plt.title("Efficient Frontier")
    plt.xlabel("Volatility")
    plt.ylabel("Expected Return")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig("../results/efficient_frontier.png", dpi=300)
    plt.show()

    # ==============================
    # Return Distribution vs Normal
    # ==============================

    all_returns = returns_df.values.flatten()

    plt.figure(figsize=(10,6))

    plt.hist(all_returns, bins=60, density=True, alpha=0.6, label="Simulated Returns")

    mu = np.mean(all_returns)
    sigma = np.std(all_returns)

    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 200)
    normal_pdf = stats.norm.pdf(x, mu, sigma)

    plt.plot(x, normal_pdf, linewidth=2, label="Normal Distribution")

    plt.title("Return Distribution vs Normal")
    plt.xlabel("Returns")
    plt.ylabel("Density")
    plt.grid(True, alpha=0.3)

    plt.legend()
    plt.savefig("../results/sharpe_distribution.png", dpi=300)
    plt.show()

    # ==============================
    # Drawdown Analysis
    # ==============================

    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max

    plt.figure(figsize=(10,6))

    plt.plot(drawdown, label="Drawdown")
    plt.title("Portfolio Drawdown")
    plt.xlabel("Time")
    plt.ylabel("Drawdown")
    plt.grid(True, alpha=0.3)

    plt.legend()
    plt.savefig("../results/drawdown.png", dpi=300)
    plt.show()

    # ==============================
    # Portfolio Growth
    # ==============================

    plt.figure(figsize=(10,6))

    plt.plot(cum_returns, label="Portfolio Growth")

    plt.title("Portfolio Growth")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Return")
    plt.grid(True, alpha=0.3)

    plt.legend()
    plt.savefig("../results/portfolio_growth.png", dpi=300)
    plt.show()


# ==============================
# Run Program
# ==============================

if __name__ == "__main__":
    main()