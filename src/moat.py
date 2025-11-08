def moat_score(fund):
    score = 0
    if fund.get("roic", 0) and fund["roic"] > 15:
        score += 40
    if fund.get("gross_margin", 0) and fund["gross_margin"] > 40:
        score += 30
    if fund.get("fcf_last", 0) and fund.get("total_debt", 1) and fund["fcf_last"] > fund["total_debt"]:
        score += 30
    return min(score, 100)
