import numpy as np


# ==================================
# Minimum Variance Portfolio
# ==================================

def min_variance_weights(returns_df):

    cov_matrix = returns_df.cov().values
    n_assets = cov_matrix.shape[0]

    ones = np.ones(n_assets)

    inv_cov = np.linalg.pinv(cov_matrix)

    weights = inv_cov @ ones
    weights = weights / (ones.T @ inv_cov @ ones)

    return weights


# ==================================
# Risk Parity Portfolio
# ==================================

import numpy as np

# ==================================
# Maximum Drawdown
# ==================================

def max_drawdown(cumulative_returns):
    """
    Calculates maximum drawdown from a cumulative return series
    """

    running_max = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - running_max) / running_max

    return drawdown.min()

def risk_parity_weights(returns_df, max_iter=1000, tol=1e-6):

    cov = returns_df.cov().values
    n = cov.shape[0]

    weights = np.ones(n) / n

    for _ in range(max_iter):

        portfolio_var = weights.T @ cov @ weights
        marginal_risk = cov @ weights
        risk_contribution = weights * marginal_risk

        target = portfolio_var / n

        diff = risk_contribution - target

        if np.sum(np.abs(diff)) < tol:
            break

        weights = weights - 0.01 * diff
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)

    return weights