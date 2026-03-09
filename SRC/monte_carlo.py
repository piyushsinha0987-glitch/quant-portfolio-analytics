import numpy as np
import pandas as pd

np.random.seed(42)

true_corr = 0.9

vols = np.array([0.15, 0.18, 0.20])

corr_matrix = np.full((3,3), true_corr)
np.fill_diagonal(corr_matrix,1)

cov_matrix_true = np.outer(vols, vols) * corr_matrix


def simulate_joint_returns(symbols, days=252):

    n_assets = len(symbols)

    vols = np.random.uniform(0.12, 0.25, n_assets)

    corr_matrix = np.full((n_assets, n_assets), 0.9)
    np.fill_diagonal(corr_matrix, 1)

    cov_matrix_true = np.outer(vols, vols) * corr_matrix

    base_mu = np.random.uniform(0.07, 0.12, n_assets) / 252

    mu = np.random.normal(
        base_mu,
        0.02/252,
        size=n_assets
    )

    z = np.random.multivariate_normal(
        np.zeros(n_assets),
        cov_matrix_true/252,
        size=days
    )

    chi = np.random.chisquare(df=5, size=days)
    scale = np.sqrt(5/chi)

    returns = mu + z * scale[:, None]

    return pd.DataFrame(returns, columns=symbols)