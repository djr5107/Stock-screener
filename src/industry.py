import yfinance as yf

SECTOR_ETFS = {
    "Technology": "XLK", "Health Care": "XLV", "Financials": "XLF",
    "Consumer Discretionary": "XLY", "Communication Services": "XLC",
    "Industrials": "XLI", "Consumer Staples": "XLP", "Energy": "XLE",
    "Utilities": "XLU", "Real Estate": "XLRE", "Materials": "XLB"
}

def sector_growth(sector):
    etf = SECTOR_ETFS.get(sector, "SPY")
    try:
        data = yf.download(etf, period="3y", progress=False)["Close"]
        return ((data.iloc[-1] / data.iloc[0]) ** (1/3) - 1) * 100
    except:
        return 0
