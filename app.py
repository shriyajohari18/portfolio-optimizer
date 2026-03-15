import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from llm import parse_risk_profile
from optimizer import optimize

st.set_page_config(
    page_title="AI Portfolio Optimizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3d4270;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #7c83fd;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
    h1 { color: #ffffff; }
    h2, h3 { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.markdown("# AI Portfolio Optimizer")
st.markdown("##### Describe your goals in plain English. AI builds your optimal portfolio.")
st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_area(
        "Describe your investment goals",
        placeholder="E.g. I am 28 years old, want to grow wealth for retirement in 30 years. I can handle moderate risk and I like tech and clean energy stocks.",
        height=130
    )
with col2:
    ticker_input = st.text_input(
        "Stocks to consider (comma-separated)",
        value="AAPL, MSFT, GOOGL, TSLA, NVDA, JPM, V, XOM"
    )
    st.caption("Add or remove any stock tickers you want to include")

run = st.button("Optimize My Portfolio")

if run:
    if not user_input.strip():
        st.warning("Please describe your investment goals first!")
    else:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        with st.spinner("Analyzing your goals with AI..."):
            try:
                profile = parse_risk_profile(user_input)
            except Exception as e:
                st.error(f"AI error: {e}")
                st.stop()

        st.markdown("---")
        st.markdown("### Your Risk Profile")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{profile['risk_level']}/10</div>
                <div class='metric-label'>Risk Level</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{profile['time_horizon'].capitalize()}</div>
                <div class='metric-label'>Time Horizon</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(profile['max_single_stock']*100)}%</div>
                <div class='metric-label'>Max Single Stock</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            sectors = ", ".join(profile['preferred_sectors']) if profile['preferred_sectors'] else "Diversified"
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value' style='font-size:1rem'>{sectors}</div>
                <div class='metric-label'>Preferred Sectors</div>
            </div>""", unsafe_allow_html=True)

        st.info(f"AI Interpretation: {profile['summary']}")

        with st.spinner("Fetching market data and optimizing portfolio..."):
            try:
                result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
            except Exception as e:
                st.error(f"Optimization error: {e}")
                st.stop()

        st.markdown("---")
        st.markdown("### Portfolio Performance")

        p1, p2, p3 = st.columns(3)
        p1.metric("Expected Annual Return", f"{result['expected_return']}%",
                  delta=f"{round(result['expected_return'] - 10, 1)}% vs market avg")
        p2.metric("Expected Volatility", f"{result['volatility']}%")
        p3.metric("Sharpe Ratio", result['sharpe_ratio'],
                  delta="Good" if result['sharpe_ratio'] > 1 else "Moderate")

        st.markdown("---")
        st.markdown("### Portfolio Allocation")

        left, right = st.columns([1, 1])

        with left:
            weights_df = pd.DataFrame(result["weights"].items(), columns=["Stock", "Weight"])
            weights_df["Allocation %"] = (weights_df["Weight"] * 100).round(2)
            weights_df = weights_df.sort_values("Weight", ascending=False)

            colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#43e97b",
                      "#fa709a", "#fee140", "#30cfd0"]
            fig_pie = go.Figure(data=[go.Pie(
                labels=weights_df["Stock"],
                values=weights_df["Weight"],
                hole=0.45,
                marker=dict(colors=colors[:len(weights_df)]),
                textinfo="label+percent",
                textfont=dict(size=13)
            )])
            fig_pie.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20),
                font=dict(color="white")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with right:
            st.markdown("**Allocation Breakdown**")
            st.dataframe(
                weights_df[["Stock", "Allocation %"]].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")
        st.markdown("### Historical Performance (2 Years)")

        prices = result["prices"]
        norm = prices / prices.dropna().iloc[0] * 100

        spy_data = result.get("spy_prices")
        fig_line = go.Figure()

        for col in norm.columns:
            fig_line.add_trace(go.Scatter(
                x=norm.index, y=norm[col],
                name=col, mode="lines",
                line=dict(width=1.5),
                opacity=0.7
            ))

        if spy_data is not None:
            spy_norm = spy_data / spy_data.dropna().iloc[0] * 100
            fig_line.add_trace(go.Scatter(
                x=spy_norm.index, y=spy_norm,
                name="S&P 500",
                mode="lines",
                line=dict(color="white", width=2.5, dash="dash"),
            ))

        portfolio_returns = (norm * weights_df.set_index("Stock")["Weight"]).sum(axis=1)
        fig_line.add_trace(go.Scatter(
            x=portfolio_returns.index, y=portfolio_returns,
            name="Your Portfolio",
            mode="lines",
            line=dict(color="#7c83fd", width=3),
        ))

        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(14,17,23,0.8)",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#2d3250", title="Date"),
            yaxis=dict(gridcolor="#2d3250", title="Normalized Value (Base=100)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        st.caption("Disclaimer: This app is for educational purposes only and does not constitute financial advice.")
