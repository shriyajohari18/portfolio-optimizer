import streamlit as st
import plotly.express as px
import pandas as pd
from llm import parse_risk_profile
from optimizer import optimize

st.set_page_config(page_title="AI Portfolio Optimizer", layout="wide")
st.title("AI Portfolio Optimizer")
st.caption("Describe your goals in plain English - AI handles the rest.")

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area(
        "Describe your investment goals",
        placeholder="E.g. I am 28, want to retire early, okay with some risk. Interested in tech.",
        height=120
    )

with col2:
    ticker_input = st.text_input(
        "Stocks to consider (comma-separated)",
        value="AAPL, MSFT, GOOGL, TSLA, NVDA, JPM, V, XOM"
    )

if st.button("Optimize My Portfolio", type="primary"):
    if not user_input.strip():
        st.warning("Please describe your investment goals first!")
    else:
        tickers = [t.strip().upper() for t in ticker_input.split(",")]

        with st.spinner("Analyzing your goals with AI..."):
            try:
                profile = parse_risk_profile(user_input)
            except Exception as e:
                st.error(f"AI error: {e}")
                st.stop()

        st.info(f"AI Interpretation: {profile['summary']}")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Risk Level", f"{profile['risk_level']} / 10")
        col_b.metric("Time Horizon", profile['time_horizon'].capitalize())
        col_c.metric("Max Single Stock", f"{int(profile['max_single_stock']*100)}%")

        with st.spinner("Running portfolio optimization..."):
            try:
                result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
            except Exception as e:
                st.error(f"Optimization error: {e}")
                st.stop()

        st.subheader("Optimized Allocation")

        weights_df = pd.DataFrame(result["weights"].items(), columns=["Stock", "Weight"])
        weights_df["Weight %"] = (weights_df["Weight"] * 100).round(2)
        fig_pie = px.pie(weights_df, names="Stock", values="Weight", title="Portfolio Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Expected Annual Return", f"{result['expected_return']}%")
        m2.metric("Expected Volatility", f"{result['volatility']}%")
        m3.metric("Sharpe Ratio", result['sharpe_ratio'])

        st.subheader("Historical Prices 2Y")
        norm_prices = result["prices"] / result["prices"].iloc[0] * 100
        fig_line = px.line(norm_prices, title="Normalized Price History")
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("Allocation Breakdown")
        st.dataframe(weights_df.sort_values("Weight", ascending=False), use_container_width=True)
