import yfinance as yf
import pandas as pd
from sec_api import XbrlApi
import os
from .utils import cache

xbrl_api = XbrlApi(api_key=os.getenv("SEC_API_KEY"))

@cache("fund")
def get_fundamentals(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info

    # Income Statement
    income = stock.financials.T
    revenue = income.get("Total Revenue", pd.Series())
    net_income = income.get("Net Income", pd.Series())

    rev_growth = revenue.pct_change().iloc[-3:].mean() * 100 if len(revenue) > 3 else 0
    eps_growth = net_income.pct_change().iloc[-3:].mean() * 100 if len(net_income) > 3 else 0

    # Balance Sheet
    bs = stock.balance_sheet.T
    total_debt = bs.get("Long Term Debt", 0) + bs.get("Short Long Term Debt", 0)
    total_debt = total_debt.iloc[-1] if len(total_debt) else 0

    fcf = stock.cashflow.T.get("Free Cash Flow")
    fcf_last = fcf.iloc[-1] if len(fcf) else 0

    # XBRL: Gross Margin & ROIC (safe fallback)
    gross_margin = roic = None
    try:
        filings = stock.sec_filings
        if filings:
            cik = str(info.get("cik", "")).zfill(10)
            accession = filings[0]["accessionNumber"].replace("-", "")
            xbrl = xbrl_api.xbrl_to_json(cik=cik, accession_no=accession)
            facts = xbrl.get("facts", {}).get("us-gaap", {})

            gross_profit = next((v["value"] for v in facts.get("GrossProfit", {}).get("values", []) if v.get("form") == "10-K"), None)
            revenues = next((v["value"] for v in facts.get("Revenues", {}).get("values", []) if v.get("form") == "10-K"), None)
            if gross_profit and revenues:
                gross_margin = gross_profit / revenues * 100

            operating_income = next((v["value"] for v in facts.get("OperatingIncomeLoss", {}).get("values", []) if v.get("form") == "10-K"), None)
            invested_capital = info.get("totalAssets", 0) - info.get("totalCurrentLiabilities", 0)
            if operating_income and invested_capital:
                roic = operating_income / invested_capital * 100
    except:
        pass

    return {
        "ticker": ticker,
        "revenue_growth": rev_growth,
        "eps_growth": eps_growth,
        "fcf_last": fcf_last,
        "total_debt": total_debt,
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "forward_pe": info.get("forwardPE"),
        "sector": info.get("sector"),
        "gross_margin": gross_margin,
        "roic": roic,
    }
