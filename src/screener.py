import pandas as pd
from .fundamentals import get_fundamentals
from .technicals import get_technicals
from .sentiment import get_sentiment
from .industry import sector_growth
from .moat import moat_score

def screen(tickers, weights):
    rows = []
    for t in tickers:
        try:
            fund = get_fundamentals(t)
            tech = get_technicals(t)
            sent = get_sentiment(t)
            ind = sector_growth(fund["sector"])
            moat = moat_score(fund)

            score = 0
            score += weights["growth"] if fund["revenue_growth"] >= 12 and fund["eps_growth"] >= 10 else 0
            score += weights["fcf"] if fund["fcf_last"] > fund["total_debt"] else 0
            score += weights["industry"] if ind > 8 else 0
            score += weights["moat"] if moat >= 60 else 0
            score += weights["value"] if (fund["ev_ebitda"] or 999) < 15 or (fund["forward_pe"] or 999) < 18 else 0
            score += weights["tech"] if tech["above_sma50"] and tech["golden_cross"] and tech["rsi14"] < 70 else 0
            score += weights["sentiment"] if sent["sentiment_score"] > 1 else 0

            signal = "STRONG BUY" if score >= 75 else "BUY" if score >= 60 else "SELL" if score <= 30 else "HOLD"

            rows.append({
                **fund, **tech, **sent,
                "sector_growth": ind, "moat_score": moat,
                "composite_score": score, "signal": signal
            })
        except Exception as e:
            print(f"Error with {t}: {e}")
            continue
    return pd.DataFrame(rows).sort_values("composite_score", ascending=False)
