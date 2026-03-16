import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from llm import parse_risk_profile
from optimizer import optimize

st.set_page_config(
    page_title="Folio AI - Smart Portfolio Optimizer",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3d4270;
        text-align: center;
        height: 100%;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #7c83fd;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    .metric-explain {
        font-size: 0.75rem;
        color: #6ee7b7;
        margin-top: 8px;
        font-style: italic;
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
    }
    .stButton > button:hover { opacity: 0.85; }
    .example-chip {
        background: #1e2130;
        border: 1px solid #3d4270;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.8rem;
        color: #9ca3af;
        display: inline-block;
        margin: 4px;
        cursor: pointer;
    }
    .footer {
        text-align: center;
        padding: 24px 0 8px 0;
        color: #4b5563;
        font-size: 0.82rem;
        border-top: 1px solid #1e2130;
        margin-top: 40px;
    }
    .footer a { color: #7c83fd; text-decoration: none; }
    h1, h2, h3 { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

SECTOR_TICKERS = {
    "tech": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
    "finance": ["JPM", "BAC", "GS", "V", "MA"],
    "energy": ["XOM", "CVX", "BP", "SLB", "COP"],
    "clean energy": ["ENPH", "NEE", "SEDG", "BEP", "FSLR"],
    "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
    "consumer": ["AMZN", "WMT", "PG", "KO", "MCD"],
    "real estate": ["AMT", "PLD", "CCI", "EQIX", "SPG"],
    "default": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "JPM", "V", "XOM"]
}

EXAMPLES = [
    "I am 25, just started working, want high growth for retirement in 30 years. Love tech.",
    "I am 40, moderate risk, interested in healthcare and consumer stocks for 10 years.",
    "I am 60, retiring soon, want very safe investments with low volatility.",
    "I am 30, interested in clean energy and ESG stocks, medium risk tolerance."
]

def suggest_tickers(user_text, preferred_sectors):
    tickers = set()
    text_lower = user_text.lower()
    for sector in preferred_sectors:
        for key in SECTOR_TICKERS:
            if key in sector.lower() or sector.lower() in key:
                tickers.update(SECTOR_TICKERS[key])
    for key in SECTOR_TICKERS:
        if key in text_lower:
            tickers.update(SECTOR_TICKERS[key])
    if not tickers:
        tickers.update(SECTOR_TICKERS["default"])
    return list(tickers)[:10]

def get_sharpe_label(s):
    if s >= 2: return "Excellent risk-adjusted return"
    if s >= 1: return "Good risk-adjusted return"
    if s >= 0.5: return "Moderate risk-adjusted return"
    return "Below average — consider diversifying more"

def get_volatility_label(v):
    if v < 10: return "Low — small price swings expected"
    if v < 20: return "Moderate — portfolio may swing up or down by this % per year"
    if v < 30: return "High — expect significant price swings"
    return "Very high — this portfolio carries substantial risk"

def get_return_label(r):
    if r > 15: return "Strong — well above the ~10% historical S&P 500 average"
    if r > 10: return "Good — above the ~10% historical S&P 500 average"
    if r > 5: return "Moderate — below market average but positive"
    return "Low — consider a higher-risk allocation for better growth"

# ── HEADER ──
st.markdown("# Folio AI")
st.markdown("##### Your personal AI-powered portfolio optimizer. Describe your goals — we handle the math.")

st.warning("This tool is for educational purposes only and does not constitute financial advice. Always consult a qualified financial advisor before investing.")
st.markdown("---")

# ── ONBOARDING ──
with st.expander("How does this work? (click to learn)", expanded=False):
    st.markdown("""
    **3 simple steps:**
    1. Describe your investment goals in plain English below — your age, risk appetite, time horizon and interests
    2. Optionally add your own stock tickers, or let AI suggest them based on your goals
    3. Click Optimize — we run Modern Portfolio Theory math on real market data to find your ideal allocation

    **What you get:**
    - A personalized risk profile based on your goals
    - An optimized portfolio with exact % allocations
    - Expected annual return, volatility and Sharpe Ratio
    - 2 years of historical performance vs the S&P 500
    """)

# ── EXAMPLE PROMPTS ──
st.markdown("**Try an example:**")
cols = st.columns(4)
for i, example in enumerate(EXAMPLES):
    with cols[i]:
        if st.button(f"Example {i+1}", key=f"ex_{i}"):
            st.session_state["prefill"] = example

# ── INPUTS ──
st.markdown("---")
col1, col2 = st.columns([2, 1])

prefill = st.session_state.get("prefill", "")

with col1:
    user_input = st.text_area(
        "Describe your investment goals",
        value=prefill,
        placeholder="E.g. I am 28, want to grow wealth for a house deposit in 5 years. I can handle moderate risk and I like tech and clean energy stocks.",
        height=130
    )
with col2:
    st.markdown("**Stocks to consider (optional)**")
    st.caption("Leave blank to let AI pick based on your goals. Add .NS for Indian stocks e.g. RELIANCE.NS")
    ticker_input = st.text_input(
        "Custom tickers",
        placeholder="E.g. AAPL, MSFT, TSLA or RELIANCE.NS, TCS.NS"
    )

run = st.button("Optimize My Portfolio")

# ── MAIN LOGIC ──
if run:
    if not user_input.strip():
        st.warning("Please describe your investment goals first!")
        st.stop()

    tickers_raw = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    with st.spinner("Step 1 of 3 — Analyzing your goals with AI..."):
        try:
            profile = parse_risk_profile(user_input)
        except Exception as e:
            st.error(f"AI error: {e}. Please try again in a moment.")
            st.stop()

    if tickers_raw:
        tickers = tickers_raw
        st.info(f"Using your custom tickers: {', '.join(tickers)}")
    else:
        tickers = suggest_tickers(user_input, profile.get("preferred_sectors", []))
        st.info(f"AI selected these stocks based on your goals: {', '.join(tickers)}")

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

    st.success(f"AI Interpretation: {profile['summary']}")

    with st.spinner("Step 2 of 3 — Fetching live market data for all stocks..."):
        pass

    with st.spinner("Step 3 of 3 — Running portfolio optimization across thousands of combinations..."):
        try:
            result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
        except Exception as e:
            st.error(f"Optimization error: {e}. Please check your tickers are valid and try again.")
            st.stop()

    st.markdown("---")
    st.markdown("### Portfolio Performance")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['expected_return']}%</div>
            <div class='metric-label'>Expected Annual Return</div>
            <div class='metric-explain'>{get_return_label(result['expected_return'])}</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['volatility']}%</div>
            <div class='metric-label'>Expected Volatility</div>
            <div class='metric-explain'>{get_volatility_label(result['volatility'])}</div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['sharpe_ratio']}</div>
            <div class='metric-label'>Sharpe Ratio</div>
            <div class='metric-explain'>{get_sharpe_label(result['sharpe_ratio'])}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Portfolio Allocation")

    weights_df = pd.DataFrame(result["weights"].items(), columns=["Stock", "Weight"])
    weights_df["Allocation %"] = (weights_df["Weight"] * 100).round(2)
    weights_df = weights_df.sort_values("Weight", ascending=False).reset_index(drop=True)

    left, right = st.columns([1, 1])
    colors = ["#667eea","#764ba2","#f093fb","#4facfe","#43e97b","#fa709a","#fee140","#30cfd0","#a18cd1","#fbc2eb"]

    with left:
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
            weights_df[["Stock", "Allocation %"]],
            use_container_width=True,
            hide_index=True
        )
        st.caption("Suggested allocation based on Sharpe Ratio maximization")

    st.markdown("---")
    st.markdown("### Historical Performance (2 Years)")

    prices = result["prices"]
    norm = prices / prices.dropna().iloc[0] * 100
    fig_line = go.Figure()

    for col in norm.columns:
        fig_line.add_trace(go.Scatter(
            x=norm.index, y=norm[col],
            name=col, mode="lines",
            line=dict(width=1.5), opacity=0.6
        ))

    spy_data = result.get("spy_prices")
    if spy_data is not None and not spy_data.empty:
        spy_norm = spy_data / spy_data.dropna().iloc[0] * 100
        fig_line.add_trace(go.Scatter(
            x=spy_norm.index, y=spy_norm.values,
            name="S&P 500 Benchmark",
            mode="lines",
            line=dict(color="white", width=2.5, dash="dash")
        ))

    weight_series = weights_df.set_index("Stock")["Weight"]
    common = norm.columns.intersection(weight_series.index)
    portfolio_line = (norm[common] * weight_series[common]).sum(axis=1)
    fig_line.add_trace(go.Scatter(
        x=portfolio_line.index, y=portfolio_line,
        name="Your Portfolio",
        mode="lines",
        line=dict(color="#7c83fd", width=3)
    ))

    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,23,0.8)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#2d3250", title="Date"),
        yaxis=dict(gridcolor="#2d3250", title="Normalized Value (Base = 100)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.caption("White dashed line = S&P 500 benchmark. Purple line = your optimized portfolio.")

    st.markdown("---")
    st.markdown("### Was this helpful?")
    fb1, fb2, fb3 = st.columns([1, 1, 4])
    with fb1:
        if st.button("👍 Yes, loved it"):
            st.success("Thank you for your feedback!")
    with fb2:
        if st.button("👎 Needs work"):
            feedback = st.text_input("What could be better?", key="feedback_text")
            if feedback:
                st.success("Thank you! We will use this to improve.")

    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        Built by <strong>Shriya Johari</strong> — Product Manager<br>
        <a href='https://github.com/shriyajohari18/portfolio-optimizer' target='_blank'>GitHub</a> &nbsp;|&nbsp;
        <a href='https://www.linkedin.com/in/shriya-johari-807736178/' target='_blank'>LinkedIn</a>
        <br><br>
        This tool is for educational purposes only and does not constitute financial advice.
        Past performance does not guarantee future results.
    </div>
    """, unsafe_allow_html=True)
