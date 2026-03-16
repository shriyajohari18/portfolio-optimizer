import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from llm import parse_risk_profile
from optimizer import optimize

st.set_page_config(
    page_title="Folio AI — Smart Portfolio Optimiser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    .hero-diff {
        font-size: 0.9rem;
        color: #7c83fd;
        background: #1a1d2e;
        border-left: 3px solid #7c83fd;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3d4270;
        text-align: center;
        height: 100%;
        margin-bottom: 8px;
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
    .metric-outcome {
        font-size: 0.78rem;
        color: #6ee7b7;
        margin-top: 10px;
        padding: 6px 10px;
        background: rgba(110,231,183,0.08);
        border-radius: 6px;
        line-height: 1.4;
    }
    .next-steps {
        background: #1e2130;
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid #3d4270;
        margin-top: 16px;
    }
    .next-steps h4 {
        color: #ffffff;
        margin-bottom: 12px;
        font-size: 1rem;
    }
    .next-step-item {
        color: #9ca3af;
        font-size: 0.88rem;
        padding: 6px 0;
        border-bottom: 1px solid #2d3250;
    }
    .trust-box {
        background: #1a1d2e;
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid #2d3250;
        margin-top: 16px;
    }
    .trust-box h4 { color: #ffffff; font-size: 1rem; margin-bottom: 12px; }
    .trust-item {
        color: #9ca3af;
        font-size: 0.85rem;
        padding: 5px 0;
        display: flex;
        gap: 10px;
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
    .footer {
        text-align: center;
        padding: 28px 0 8px 0;
        color: #4b5563;
        font-size: 0.82rem;
        border-top: 1px solid #1e2130;
        margin-top: 48px;
    }
    .footer a { color: #7c83fd; text-decoration: none; }
    .error-box {
        background: #2d1f1f;
        border: 1px solid #7f1d1d;
        border-radius: 8px;
        padding: 14px 18px;
        color: #fca5a5;
        font-size: 0.9rem;
        margin: 8px 0;
    }
    .mobile-note {
        background: #1e2130;
        border: 1px solid #3d4270;
        border-radius: 8px;
        padding: 10px 16px;
        color: #9ca3af;
        font-size: 0.82rem;
        text-align: center;
    }
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
    "I am 25, just started working, want high growth over 30 years. I love tech stocks and can handle high risk.",
    "I am 40, moderate risk, interested in healthcare and consumer stocks for the next 10 years.",
    "I am 60, retiring soon, want very safe low-volatility investments to preserve my wealth.",
    "I am 30, passionate about clean energy and ESG investing, medium risk tolerance, 15-year horizon."
]

ERROR_MESSAGES = {
    "429": "Our AI is taking a short break due to high demand. Please wait 30 seconds and try again.",
    "403": "There was an authentication issue with our AI service. Please try again shortly.",
    "404": "We could not reach our AI service. Please try again in a moment.",
    "400": "We had trouble understanding your request. Please try rephrasing your goals.",
    "default": "Something went wrong. Please try again — if the problem persists, try refreshing the page."
}

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

def friendly_error(e):
    msg = str(e)
    for code, friendly in ERROR_MESSAGES.items():
        if code in msg:
            return friendly
    return ERROR_MESSAGES["default"]

def get_sharpe_outcome(s):
    if s >= 2: return "Excellent. For every unit of risk you take on, you earn 2+ units of return."
    if s >= 1: return "Good. You are being well-rewarded relative to the risk you are taking."
    if s >= 0.5: return "Moderate. Your returns are reasonable but there may be better allocations."
    return "Below average. Consider diversifying into less correlated assets."

def get_volatility_outcome(v):
    if v < 10: return f"Low risk. In a difficult year, your portfolio could fall by roughly {v:.0f}%."
    if v < 20: return f"Moderate risk. Your portfolio could swing up or down by about {v:.0f}% in any given year."
    if v < 30: return f"High risk. Expect significant price movements — up to {v:.0f}% in either direction annually."
    return f"Very high risk. This portfolio could move by {v:.0f}% or more in a year. Only suitable for aggressive investors."

def get_return_outcome(r):
    diff = r - 10
    direction = "above" if diff >= 0 else "below"
    if r > 15: return f"Strong. This is {abs(diff):.1f}% {direction} the historical S&P 500 average of ~10% per year."
    if r > 10: return f"Good. This is {abs(diff):.1f}% {direction} the historical S&P 500 average of ~10% per year."
    if r > 5: return f"Moderate. This is {abs(diff):.1f}% {direction} the historical S&P 500 average. Consider a higher-risk allocation."
    return "Low. This portfolio may not keep pace with inflation. Consider adjusting your risk level."

# ── HERO SECTION ──
st.markdown("""
<div class='hero-title'>Folio AI</div>
<div class='hero-sub'>Tell us your goals. We build your perfect investment portfolio in under 60 seconds.</div>
<div class='hero-diff'>Unlike generic AI chatbots, Folio AI uses real historical market data and mathematical optimisation — not guesswork.</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='mobile-note'>
For the best experience, please open this on a desktop or laptop browser.
</div>
""", unsafe_allow_html=True)

st.markdown("")

st.warning("This tool is for educational purposes only and does not constitute financial advice. Past performance does not guarantee future results. Always consult a qualified financial adviser before investing.")

st.markdown("---")

# ── HOW IT WORKS ──
with st.expander("How does Folio AI work?", expanded=False):
    st.markdown("""
    **Three simple steps:**

    1. **Describe your goals** in plain English — your age, how long you want to invest, how much risk you can stomach, and any sectors you find interesting.
    2. **We select stocks** automatically based on your goals, or you can enter your own tickers.
    3. **We optimise your portfolio** using Modern Portfolio Theory — the same mathematical framework used by professional fund managers.

    **What you receive:**
    - A personalised risk profile based on your goals
    - An optimised portfolio with exact percentage allocations
    - Plain English explanations of every metric
    - Two years of historical performance compared to the S&P 500

    **How we calculate this:**
    - We fetch two years of real adjusted close price data from Yahoo Finance
    - We calculate annualised returns and volatility for each stock
    - We use a Sharpe Ratio maximisation algorithm (SciPy SLSQP) to find the optimal allocation
    - We use Google Gemini AI to understand your goals and extract your risk profile

    **Limitations to be aware of:**
    - This tool uses historical data — past performance does not guarantee future returns
    - The optimisation is based on the stocks you select, not the entire market
    - This is an educational tool, not regulated financial advice
    """)

st.markdown("---")

# ── EXAMPLE PROMPTS ──
st.markdown("**Try an example to get started:**")
ex_cols = st.columns(4)
for i, example in enumerate(EXAMPLES):
    with ex_cols[i]:
        label = ["Young & Ambitious", "Mid-Career", "Near Retirement", "ESG Investor"][i]
        if st.button(label, key=f"ex_{i}"):
            st.session_state["prefill"] = example

st.markdown("---")

# ── INPUTS ──
col1, col2 = st.columns([2, 1])
prefill = st.session_state.get("prefill", "")

with col1:
    user_input = st.text_area(
        "Describe your investment goals",
        value=prefill,
        placeholder="E.g. I am 28, want to build wealth for a house deposit in 5 years. I can handle moderate risk and I am interested in tech and clean energy stocks.",
        height=130
    )

with col2:
    st.markdown("**Stocks to consider (optional)**")
    st.caption("Leave blank and AI will suggest stocks based on your goals. For Indian stocks, add .NS — e.g. RELIANCE.NS, TCS.NS")
    ticker_input = st.text_input(
        "Custom tickers",
        placeholder="E.g. AAPL, MSFT, TSLA"
    )

run = st.button("Optimise My Portfolio")

# ── MAIN LOGIC ──
if run:
    if not user_input.strip():
        st.warning("Please describe your investment goals first.")
        st.stop()

    tickers_raw = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    with st.spinner("Step 1 of 3 — Reading your goals and building your risk profile..."):
        try:
            profile = parse_risk_profile(user_input)
        except Exception as e:
            st.markdown(f"<div class='error-box'>{friendly_error(e)}</div>", unsafe_allow_html=True)
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

    with st.spinner("Step 2 of 3 — Fetching two years of live market data for all stocks..."):
        pass

    with st.spinner("Step 3 of 3 — Running optimisation across thousands of portfolio combinations..."):
        try:
            result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
        except Exception as e:
            err = str(e)
            if "valid ticker" in err.lower() or "2 valid" in err.lower():
                st.markdown("<div class='error-box'>We could not find enough valid stock data. Please check your tickers are correct and try again. Make sure Indian stocks include .NS (e.g. RELIANCE.NS).</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-box'>Optimisation error: {err}. Please check your tickers are valid and try again.</div>", unsafe_allow_html=True)
            st.stop()

    st.markdown("---")
    st.markdown("### Portfolio Performance")
    st.caption("Here is what these numbers mean for you in plain English.")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['expected_return']}%</div>
            <div class='metric-label'>Expected Annual Return</div>
            <div class='metric-outcome'>{get_return_outcome(result['expected_return'])}</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['volatility']}%</div>
            <div class='metric-label'>Expected Volatility</div>
            <div class='metric-outcome'>{get_volatility_outcome(result['volatility'])}</div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{result['sharpe_ratio']}</div>
            <div class='metric-label'>Sharpe Ratio</div>
            <div class='metric-outcome'>{get_sharpe_outcome(result['sharpe_ratio'])}</div>
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
        st.caption("Allocations calculated to maximise risk-adjusted return (Sharpe Ratio) within your risk constraints.")

        portfolio_url = f"https://portfolio-optimizer-uihgtnmomrcsl2ptkclwts.streamlit.app"
        st.markdown(f"**Share this tool:**")
        st.code(portfolio_url, language=None)

    st.markdown("---")
    st.markdown("### Historical Performance (2 Years)")
    st.caption("See how these stocks performed historically. The purple line shows your optimised portfolio. The white dashed line is the S&P 500 benchmark.")

    prices = result["prices"]
    norm = prices / prices.dropna().iloc[0] * 100
    fig_line = go.Figure()

    for col in norm.columns:
        fig_line.add_trace(go.Scatter(
            x=norm.index, y=norm[col],
            name=col, mode="lines",
            line=dict(width=1.5), opacity=0.5
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
        yaxis=dict(gridcolor="#2d3250", title="Normalised Value (Base = 100)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.markdown("### What to do next")
    st.markdown("""
    <div class='next-steps'>
        <h4>Suggested next steps</h4>
        <div class='next-step-item'>1. Screenshot or note down your allocation percentages above</div>
        <div class='next-step-item'>2. Open your brokerage account (e.g. Freetrade, Trading 212, Hargreaves Lansdown)</div>
        <div class='next-step-item'>3. Search for each stock ticker and invest your chosen amount in the suggested proportions</div>
        <div class='next-step-item'>4. Review and rebalance your portfolio every 6 to 12 months</div>
        <div class='next-step-item'>5. Try adjusting your risk level or time horizon to see different allocations</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Was this useful?")
    st.caption("Your feedback helps us improve Folio AI.")
    fb1, fb2 = st.columns([1, 1])
    with fb1:
        if st.button("Yes, this was helpful"):
            st.success("Thank you — we are glad it was useful!")
    with fb2:
        if st.button("No, something needs improving"):
            feedback = st.text_area("What could be better? We read every response.", key="feedback_text", height=80)
            if feedback:
                st.success("Thank you for your feedback. We will review it shortly.")

    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        <strong style='color:#7c83fd; font-size:1rem;'>Folio AI</strong><br><br>
        Built by <strong>Shriya Johari</strong> — Product Manager<br>
        <a href='https://github.com/shriyajohari18/portfolio-optimizer' target='_blank'>GitHub</a>
        &nbsp;|&nbsp;
        <a href='https://www.linkedin.com/in/shriya-johari-807736178/' target='_blank'>LinkedIn</a>
        <br><br>
        This tool is for educational purposes only and does not constitute financial advice.<br>
        Past performance does not guarantee future results.<br>
        Always consult a qualified financial adviser before making investment decisions.
        <br><br>
        Data sourced from Yahoo Finance. AI powered by Google Gemini.
        Optimisation engine built with SciPy and Modern Portfolio Theory.
    </div>
    """, unsafe_allow_html=True)
