import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

def fetch_data(tickers: list, period: str = "2y") -> pd.DataFrame:
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    else:
        data = data[["Close"]] if "Close" in data.columns else data
    return data.dropna()

def compute_stats(prices: pd.DataFrame):
    returns = prices.pct_change().dropna()
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    return mean_returns, cov_matrix

def portfolio_performance(weights, mean_returns, cov_matrix):
    weights = np.array(weights)
    ret = np.dot(weights, mean_returns)
    vol = np.sqrt(np.dot(weights, np.dot(cov_matrix.values, weights)))
    sharpe = ret / vol if vol != 0 else 0
    return ret, vol, sharpe

def optimize(tickers, risk_level, max_single_stock=0.4):
    prices = fetch_data(tickers)

    if prices.shape[1] < 2:
        raise ValueError("Need at least 2 valid tickers with price data.")

    mean_returns, cov_matrix = compute_stats(prices)
    n = len(prices.columns)

    def neg_sharpe(weights):
        _, _, sharpe = portfolio_performance(weights, mean_returns, cov_matrix)
        return -sharpe

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0.01, max_single_stock)] * n

    result = minimize(
        neg_sharpe,
        x0=np.array([1/n] * n),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    weights = result.x
    tickers_used = list(prices.columns)
    ret, vol, sharpe = portfolio_performance(weights, mean_returns, cov_matrix)

    return {
        "weights": dict(zip(tickers_used, weights.round(4))),
        "expected_return": round(ret * 100, 2),
        "volatility": round(vol * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "prices": prices
    }
