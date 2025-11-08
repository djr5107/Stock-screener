import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def backtest_strategy(tickers, months=12):
    end = datetime.now()
    start = end - timedelta(days=months * 35)
    data = yf.download(tickers, start=start, end=end, progress=False)["Adj Close"]
    portfolio = (data.pct_change().mean(axis=1).fillna(0) + 1).cumprod()
    portfolio.name = "Portfolio Value"
    return pd.DataFrame({"portfolio": portfolio})
