import yfinance as yf
import pandas as pd
from .utils import cache

@cache("tech")
def get_technicals(ticker: str) -> dict:
    df = yf.download(ticker, period="2y", progress=False, auto_adjust=True)
    close = df["Close"]

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1]

    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = up.rolling(14).mean() / down.rolling(14).mean()
    rsi = 100 - (100 / (1 + rs)).iloc[-1]

    return {
        "price": close.iloc[-1],
        "sma20": sma20,
        "sma50": sma50,
        "sma200": sma200,
        "rsi14": rsi,
        "above_sma50": close.iloc[-1] > sma50,
        "golden_cross": sma50 > sma200
    }
