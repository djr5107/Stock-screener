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
            score += weights["growth"] if fund.get("revenue_growth", 0) >= 12 and fund.get("eps_growth", 0) >= 10 else 0
            score += weights["fcf"] if fund.get("fcf_last", 0) > fund.get("total_debt", 1) else 0
            score += weights["industry"] if ind > 8 else 0
            score += weights["moat"] if moat >= 60 else 0
            score += weights["value"] if (fund.get("ev_ebitda") or 999) < 15 or (fund.get("forward_pe") or 999) < 18 else 0
            score += weights["tech"] if tech.get("above_sma50") and tech.get("golden_cross") and tech.get("rsi14", 100) < 70 else 0
            score += weights["sentiment"] if sent.get("sentiment_score", 0) > 1 else 0

            signal = "STRONG BUY" if score >= 75 else "BUY" if score >= 60 else "SELL" if score <= 30 else "HOLD"

            rows.append({
                **fund, **tech, **sent,
                "sector_growth": ind, "moat_score": moat,
                "composite_score": score, "signal": signal
            })
        except Exception as e:
            print(f"Error with {t}: {e}")
            continue

    # === FIX: Handle empty results ===
    if not rows:
        return pd.DataFrame(columns=[
            "ticker", "revenue_growth", "eps_growth", "fcf_last", "total_debt",
            "ev_ebitda", "forward_pe", "sector", "gross_margin", "roic",
            "price", "sma50", "rsi14", "sentiment_score", "mentions",
            "sector_growth", "moat_score", "composite_score", "signal"
        ])

    df = pd.DataFrame(rows)
    return df.sort_values("composite_score", ascending=False)
