import streamlit as st
import pandas as pd
from src.screener import screen
from src.backtest import backtest_strategy
import plotly.express as px

st.set_page_config(page_title="AI Stock Screener", layout="wide")
st.title("Growth + Moat + Value + Sentiment Screener")
st.markdown("**Find high-growth, cash-rich, fairly valued leaders with momentum**")

# --- Sidebar: Interactive Weights ---
st.sidebar.header("Weight Your Criteria")
w_growth = st.sidebar.slider("Top/Bottom Line Growth", 0, 30, 20)
w_fcf = st.sidebar.slider("FCF > Debt", 0, 20, 15)
w_industry = st.sidebar.slider("Growing Industry", 0, 15, 10)
w_moat = st.sidebar.slider("Moat (ROIC + Margins)", 0, 20, 15)
w_value = st.sidebar.slider("Not Overvalued", 0, 20, 15)
w_tech = st.sidebar.slider("Technical Momentum", 0, 15, 10)
w_sentiment = st.sidebar.slider("Social + News Buzz", 0, 15, 10)

# --- Universe ---
default_tickers = "AAPL MSFT GOOGL NVDA TSLA JPM V MA HD PG UNH DIS NFLX ADBE PYPL INTC AMD CRM NOW SHOP AMZN META"
user_input = st.text_area("Enter tickers (space/comma)", value=default_tickers, height=80)
tickers = [t.strip().upper() for t in user_input.replace(",", " ").split() if t.strip()]

# --- Email Alert ---
email = st.text_input("Get top 3 BUY alerts via email (optional)")
if email and st.button("Enable Email Alerts"):
    st.success(f"Alerts enabled for {email}")

# --- Run Screener ---
if st.button("Run Screener", type="primary"):
    with st.spinner("Analyzing..."):
        df = screen(tickers, weights={
            "growth": w_growth, "fcf": w_fcf, "industry": w_industry,
            "moat": w_moat, "value": w_value, "tech": w_tech, "sentiment": w_sentiment
        })

    # Results
    st.subheader(f"Results ({len(df)} stocks)")
    def color_signal(val):
        color = {"STRONG BUY": "#00ff00", "BUY": "#90EE90", "HOLD": "#D3D3D3", "SELL": "#ffcccb"}
        return f"background-color: {color.get(val, '')}"
    styled = df.style.format({
        "revenue_growth": "{:.1f}%", "eps_growth": "{:.1f}%", "roic": "{:.1f}%", "gross_margin": "{:.1f}%",
        "ev_ebitda": "{:.1f}", "forward_pe": "{:.1f}", "composite_score": "{:.0f}"
    }).applymap(color_signal, subset=["signal"])
    st.dataframe(styled, use_container_width=True)

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(df, x="forward_pe", y="revenue_growth", size="moat_score", color="signal",
                         hover_name="ticker", title="Value vs Growth")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(df.head(10), x="ticker", y="composite_score", color="signal", title="Top 10 Scores")
        st.plotly_chart(fig2, use_container_width=True)

    # Backtest
    if len(df) > 0:
        st.subheader("Backtest: Buy Top 5 Every Month")
        returns_df = backtest_strategy(df.head(5)["ticker"].tolist())
        st.line_chart(returns_df["portfolio"])

    # Download
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "results.csv", "text/csv")

    # Email top 3
    if email and df[df["signal"] == "STRONG BUY"].shape[0] > 0:
        top3 = df[df["signal"].isin(["STRONG BUY", "BUY"])].head(3)
        msg = "Subject: Strong Buy Alerts\n\n" + top3[["ticker", "signal", "composite_score"]].to_string()
        # In production: use SMTP
        st.code("Email would be sent:\n" + msg)
