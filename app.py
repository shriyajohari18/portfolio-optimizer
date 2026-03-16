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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp, .main, [data-testid="stAppViewContainer"] {
    background: #070810 !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HERO ── */
.hero {
    position: relative;
    padding: 80px 64px 60px;
    overflow: hidden;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.hero::before {
    content: '';
    position: absolute;
    top: -200px; right: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -100px; left: 30%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 24px; height: 1px;
    background: #6366f1;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(48px, 6vw, 80px);
    font-weight: 800;
    line-height: 1.0;
    color: #ffffff;
    margin-bottom: 24px;
    letter-spacing: -0.03em;
}
.hero-title span {
    background: linear-gradient(135deg, #818cf8, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 17px;
    font-weight: 300;
    color: rgba(255,255,255,0.5);
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 40px;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 100px;
    font-size: 12px;
    color: #818cf8;
    font-weight: 400;
}
.hero-stats {
    display: flex;
    gap: 48px;
    margin-top: 48px;
    padding-top: 40px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.hero-stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
}
.hero-stat-label {
    font-size: 12px;
    color: rgba(255,255,255,0.35);
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── DISCLAIMER ── */
.disclaimer {
    margin: 0 64px;
    padding: 14px 20px;
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    font-size: 12.5px;
    color: rgba(245,158,11,0.8);
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-top: 32px;
}

/* ── SECTION ── */
.section {
    padding: 48px 64px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.section-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.25);
    margin-bottom: 8px;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 32px;
    letter-spacing: -0.02em;
}

/* ── EXAMPLES ── */
.examples-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 32px;
}
.example-card {
    padding: 16px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
}
.example-card:hover {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.3);
}
.example-tag {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 8px;
}
.example-text {
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    line-height: 1.5;
}

/* ── INPUT AREA ── */
.input-grid {
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 16px;
}

/* Streamlit input overrides */
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
    resize: none !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: rgba(255,255,255,0.2) !important;
}
label[data-testid="stWidgetLabel"] p {
    color: rgba(255,255,255,0.5) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 8px !important;
}

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 40px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    width: 100% !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #818cf8, #6366f1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.3) !important;
}

/* ── PROFILE CARDS ── */
.profile-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.profile-card {
    padding: 24px 20px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.profile-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #10b981);
}
.profile-card-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
}
.profile-card-label {
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

/* ── PERFORMANCE CARDS ── */
.perf-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.perf-card {
    padding: 28px 24px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    position: relative;
    overflow: hidden;
}
.perf-card-number {
    font-family: 'Syne', sans-serif;
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
    letter-spacing: -0.03em;
}
.perf-card-label {
    font-size: 12px;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
}
.perf-card-outcome {
    font-size: 13px;
    color: rgba(255,255,255,0.55);
    line-height: 1.6;
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.perf-card-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 500;
    margin-top: 10px;
}
.badge-good { background: rgba(16,185,129,0.12); color: #10b981; }
.badge-moderate { background: rgba(245,158,11,0.12); color: #f59e0b; }
.badge-poor { background: rgba(239,68,68,0.12); color: #ef4444; }

/* ── ALLOCATION ── */
.alloc-table {
    width: 100%;
    border-collapse: collapse;
}
.alloc-table tr {
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.alloc-table tr:last-child { border-bottom: none; }
.alloc-table td {
    padding: 14px 0;
    font-size: 14px;
    color: rgba(255,255,255,0.7);
}
.alloc-bar-wrap {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    margin-top: 4px;
}
.alloc-bar {
    height: 4px;
    background: linear-gradient(90deg, #6366f1, #10b981);
    border-radius: 2px;
}
.alloc-pct {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    color: #ffffff;
}

/* ── NEXT STEPS ── */
.steps-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 8px;
}
.step-card {
    padding: 20px 16px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
}
.step-num {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: rgba(99,102,241,0.3);
    margin-bottom: 8px;
    line-height: 1;
}
.step-text {
    font-size: 12.5px;
    color: rgba(255,255,255,0.45);
    line-height: 1.6;
}

/* ── TRUST ── */
.trust-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
.trust-card {
    padding: 24px 20px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
}
.trust-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    margin-bottom: 14px;
}
.trust-title {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}
.trust-desc {
    font-size: 12.5px;
    color: rgba(255,255,255,0.4);
    line-height: 1.6;
}

/* ── FEEDBACK ── */
.feedback-row {
    display: flex;
    gap: 12px;
    margin-top: 8px;
}

/* ── FOOTER ── */
.footer {
    padding: 40px 64px;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-brand {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: rgba(255,255,255,0.15);
}
.footer-links {
    display: flex;
    gap: 24px;
    font-size: 12px;
    color: rgba(255,255,255,0.25);
}
.footer-links a {
    color: rgba(255,255,255,0.35);
    text-decoration: none;
    transition: color 0.2s;
}
.footer-links a:hover { color: #818cf8; }
.footer-legal {
    font-size: 11px;
    color: rgba(255,255,255,0.15);
    text-align: right;
    max-width: 320px;
    line-height: 1.6;
}

/* ── ALERTS ── */
.stAlert {
    background: rgba(245,158,11,0.06) !important;
    border: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: 10px !important;
    color: rgba(245,158,11,0.8) !important;
}
[data-testid="stInfo"] {
    background: rgba(99,102,241,0.06) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.06) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important;
}
.error-box {
    padding: 16px 20px;
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px;
    font-size: 13.5px;
    color: rgba(239,68,68,0.8);
    margin: 12px 0;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.5) !important;
    font-size: 13px !important;
    padding: 16px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-color: #6366f1 !important; }

/* ── PLOTLY ── */
.js-plotly-plot { border-radius: 16px; overflow: hidden; }

/* ── DIVIDER ── */
.divider {
    height: 1px;
    background: rgba(255,255,255,0.04);
    margin: 0 64px;
}

/* ── INTERPRETATION BOX ── */
.interp-box {
    padding: 20px 24px;
    background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    font-size: 14px;
    color: rgba(255,255,255,0.6);
    line-height: 1.7;
    margin-bottom: 24px;
}
.interp-box strong { color: #818cf8; font-weight: 500; }

/* ── MOBILE WARNING ── */
.mobile-warn {
    display: none;
    padding: 12px 20px;
    background: rgba(99,102,241,0.08);
    text-align: center;
    font-size: 12px;
    color: rgba(255,255,255,0.4);
}
@media (max-width: 768px) { .mobile-warn { display: block; } }
</style>
""", unsafe_allow_html=True)

# ── DATA ──
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
    ("Young & Ambitious", "I am 24, just started my first job. I want aggressive growth over 30 years and love tech stocks. High risk is fine."),
    ("Mid-Career Planner", "I am 38, stable income, two kids. I want moderate growth over 15 years — a mix of healthcare and consumer stocks."),
    ("Near Retirement", "I am 58, retiring in 5 years. I need low volatility and capital preservation. Minimal risk please."),
    ("ESG Investor", "I am 31, passionate about sustainability. I want clean energy and ESG companies, medium risk, 20-year horizon.")
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

def sharpe_badge(s):
    if s >= 1: return ("Excellent", "badge-good")
    if s >= 0.5: return ("Moderate", "badge-moderate")
    return ("Below Average", "badge-poor")

def return_badge(r):
    if r > 10: return ("Above Market", "badge-good")
    if r > 5: return ("Near Market", "badge-moderate")
    return ("Below Market", "badge-poor")

def vol_badge(v):
    if v < 15: return ("Low Risk", "badge-good")
    if v < 25: return ("Moderate Risk", "badge-moderate")
    return ("High Risk", "badge-poor")

def get_return_outcome(r):
    diff = abs(r - 10)
    dir_ = "above" if r >= 10 else "below"
    if r > 15: return f"Strong. {diff:.1f}% above the S&P 500 historical average of ~10% per year."
    if r > 10: return f"Good. {diff:.1f}% above the S&P 500 historical average of ~10% per year."
    if r > 5: return f"Moderate. {diff:.1f}% below the S&P 500 average. Consider a higher-risk allocation."
    return "Low. This portfolio may not keep pace with inflation long term."

def get_vol_outcome(v):
    if v < 10: return f"Low. In a difficult year, this portfolio could fall by roughly {v:.0f}%."
    if v < 20: return f"Moderate. Expect price swings of around {v:.0f}% in either direction annually."
    if v < 30: return f"High. This portfolio could move by up to {v:.0f}% in a year — suits risk-tolerant investors."
    return f"Very high. Potential swings of {v:.0f}%+. Only suitable for aggressive, long-term investors."

def get_sharpe_outcome(s):
    if s >= 2: return "Excellent. Every unit of risk is rewarded with 2+ units of return."
    if s >= 1: return "Good. You are being well-rewarded relative to the risk you are taking on."
    if s >= 0.5: return "Moderate. Returns are reasonable but there may be better allocations."
    return "Below average. Consider diversifying into less correlated assets."

# ── MOBILE WARNING ──
st.markdown("<div class='mobile-warn'>For the best experience, open Folio AI on a desktop browser.</div>", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div class='hero'>
    <div class='hero-eyebrow'>AI-Powered Portfolio Optimisation</div>
    <div class='hero-title'>Build your<br><span>perfect portfolio.</span></div>
    <div class='hero-sub'>Tell us your goals in plain English. We use real market data and mathematical optimisation to build your ideal investment allocation — in under 60 seconds.</div>
    <div class='hero-pill'>Unlike generic AI chatbots, Folio AI uses historical market data and Modern Portfolio Theory — not guesswork</div>
    <div class='hero-stats'>
        <div>
            <div class='hero-stat-value'>MPT</div>
            <div class='hero-stat-label'>Optimisation Engine</div>
        </div>
        <div>
            <div class='hero-stat-value'>2Y</div>
            <div class='hero-stat-label'>Historical Data</div>
        </div>
        <div>
            <div class='hero-stat-value'>Live</div>
            <div class='hero-stat-label'>Market Prices</div>
        </div>
        <div>
            <div class='hero-stat-value'>Free</div>
            <div class='hero-stat-label'>Always</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── DISCLAIMER ──
st.markdown("""
<div class='disclaimer'>
    <span>⚠</span>
    <span>This tool is for <strong>educational purposes only</strong> and does not constitute financial advice. Past performance does not guarantee future results. Always consult a qualified financial adviser before investing.</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)

# ── HOW IT WORKS ──
st.markdown("<div class='section'>", unsafe_allow_html=True)
with st.expander("How does Folio AI work?"):
    st.markdown("""
**Three steps:**
1. **Describe your goals** — your age, time horizon, risk appetite, and any sectors you care about
2. **We select stocks** automatically, or enter your own tickers
3. **We optimise** using Modern Portfolio Theory — the same framework used by professional fund managers

**What you get:** Personalised risk profile · Optimised allocations · Plain English metric explanations · 2-year performance vs S&P 500

**How we calculate this:** Real adjusted close prices from Yahoo Finance · Annualised returns and covariance matrix · Sharpe Ratio maximisation via SciPy SLSQP · Google Gemini AI for natural language understanding

**For Indian stocks:** Add .NS to any NSE ticker — e.g. RELIANCE.NS, TCS.NS, HDFCBANK.NS
    """)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── EXAMPLES ──
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>Quick Start</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Try an example</div>", unsafe_allow_html=True)

ex_cols = st.columns(4)
for i, (label, text) in enumerate(EXAMPLES):
    with ex_cols[i]:
        if st.button(label, key=f"ex_{i}"):
            st.session_state["prefill"] = text

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ── INPUTS ──
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>Step 1</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Describe your goals</div>", unsafe_allow_html=True)

prefill = st.session_state.get("prefill", "")
col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area(
        "Your investment goals",
        value=prefill,
        placeholder="E.g. I am 28, I want to build wealth for a house deposit in 5 years. I can handle moderate risk and I am interested in tech and clean energy.",
        height=140
    )

with col2:
    ticker_input = st.text_input(
        "Custom tickers (optional)",
        placeholder="E.g. AAPL, MSFT, RELIANCE.NS"
    )
    st.markdown("<div style='font-size:12px; color:rgba(255,255,255,0.25); margin-top:8px; line-height:1.6'>Leave blank and AI will suggest stocks based on your goals. Add .NS for Indian NSE stocks.</div>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
run = st.button("Optimise My Portfolio →")
st.markdown("</div>", unsafe_allow_html=True)

# ── MAIN LOGIC ──
if run:
    if not user_input.strip():
        st.warning("Please describe your investment goals first.")
        st.stop()

    tickers_raw = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    with st.spinner("Step 1 of 3 — Reading your goals and building your risk profile..."):
        try:
            profile = parse_risk_profile(user_input)
        except Exception as e:
            st.markdown(f"<div class='error-box'>{friendly_error(e)}</div>", unsafe_allow_html=True)
            st.stop()

    tickers = tickers_raw if tickers_raw else suggest_tickers(user_input, profile.get("preferred_sectors", []))
    source = "your custom tickers" if tickers_raw else "AI-selected based on your goals"
    st.info(f"Stocks selected ({source}): {', '.join(tickers)}")

    # ── RISK PROFILE ──
    st.markdown("<div class='section-label'>Your Profile</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Risk Profile</div>", unsafe_allow_html=True)

    sectors_display = ", ".join(profile.get('preferred_sectors', [])) if profile.get('preferred_sectors') else "Diversified"
    st.markdown(f"""
    <div class='profile-grid'>
        <div class='profile-card'>
            <div class='profile-card-value'>{profile['risk_level']}<span style='font-size:16px;color:rgba(255,255,255,0.3)'>/10</span></div>
            <div class='profile-card-label'>Risk Level</div>
        </div>
        <div class='profile-card'>
            <div class='profile-card-value'>{profile['time_horizon'].capitalize()}</div>
            <div class='profile-card-label'>Time Horizon</div>
        </div>
        <div class='profile-card'>
            <div class='profile-card-value'>{int(profile['max_single_stock']*100)}<span style='font-size:16px;color:rgba(255,255,255,0.3)'>%</span></div>
            <div class='profile-card-label'>Max Per Stock</div>
        </div>
        <div class='profile-card'>
            <div class='profile-card-value' style='font-size:18px'>{sectors_display}</div>
            <div class='profile-card-label'>Sectors</div>
        </div>
    </div>
    <div class='interp-box'><strong>AI says:</strong> {profile['summary']}</div>
    """, unsafe_allow_html=True)

    # ── OPTIMISE ──
    with st.spinner("Step 2 of 3 — Fetching two years of live market data..."):
        pass
    with st.spinner("Step 3 of 3 — Running optimisation across thousands of portfolio combinations..."):
        try:
            result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
        except Exception as e:
            err = str(e)
            if "2 valid" in err.lower() or "valid ticker" in err.lower():
                st.markdown("<div class='error-box'>We could not find enough valid stock data. Please check your tickers are correct. Indian stocks need .NS (e.g. RELIANCE.NS).</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-box'>Optimisation error: {err}. Please check your tickers and try again.</div>", unsafe_allow_html=True)
            st.stop()

    # ── PERFORMANCE ──
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Results</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio Performance</div>", unsafe_allow_html=True)

    r = result['expected_return']
    v = result['volatility']
    s = result['sharpe_ratio']
    rb, rc = return_badge(r)
    vb, vc = vol_badge(v)
    sb, sc = sharpe_badge(s)

    r_color = "#10b981" if r > 10 else "#f59e0b" if r > 5 else "#ef4444"
    v_color = "#10b981" if v < 15 else "#f59e0b" if v < 25 else "#ef4444"
    s_color = "#10b981" if s >= 1 else "#f59e0b" if s >= 0.5 else "#ef4444"

    st.markdown(f"""
    <div class='perf-grid'>
        <div class='perf-card'>
            <div class='perf-card-number' style='color:{r_color}'>{r}%</div>
            <div class='perf-card-label'>Expected Annual Return</div>
            <div class='perf-card-outcome'>{get_return_outcome(r)}</div>
            <div class='perf-card-badge {rc}'>{rb}</div>
        </div>
        <div class='perf-card'>
            <div class='perf-card-number' style='color:{v_color}'>{v}%</div>
            <div class='perf-card-label'>Expected Volatility</div>
            <div class='perf-card-outcome'>{get_vol_outcome(v)}</div>
            <div class='perf-card-badge {vc}'>{vb}</div>
        </div>
        <div class='perf-card'>
            <div class='perf-card-number' style='color:{s_color}'>{s}</div>
            <div class='perf-card-label'>Sharpe Ratio</div>
            <div class='perf-card-outcome'>{get_sharpe_outcome(s)}</div>
            <div class='perf-card-badge {sc}'>{sb}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ALLOCATION ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio Allocation</div>", unsafe_allow_html=True)

    weights_df = pd.DataFrame(result["weights"].items(), columns=["Stock", "Weight"])
    weights_df["Allocation %"] = (weights_df["Weight"] * 100).round(2)
    weights_df = weights_df.sort_values("Weight", ascending=False).reset_index(drop=True)

    left, right = st.columns([1, 1])
    colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#84cc16","#f97316","#ec4899","#14b8a6"]

    with left:
        fig_pie = go.Figure(data=[go.Pie(
            labels=weights_df["Stock"],
            values=weights_df["Weight"],
            hole=0.6,
            marker=dict(colors=colors[:len(weights_df)], line=dict(color='#070810', width=3)),
            textinfo="label+percent",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
        )])
        fig_pie.add_annotation(
            text=f"<b>{len(weights_df)}</b><br><span style='font-size:10px'>stocks</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="white", family="Syne")
        )
        fig_pie.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=16, b=16, l=16, r=16),
            font=dict(color="white", family="DM Sans")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with right:
        rows_html = ""
        for _, row in weights_df.iterrows():
            pct = row["Allocation %"]
            rows_html += f"""
            <tr>
                <td style='font-weight:500;color:#fff'>{row['Stock']}</td>
                <td>
                    <div class='alloc-bar-wrap'><div class='alloc-bar' style='width:{pct}%'></div></div>
                </td>
                <td style='text-align:right'><span class='alloc-pct'>{pct}%</span></td>
            </tr>"""
        st.markdown(f"<table class='alloc-table'>{rows_html}</table>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:20px; font-size:11px; color:rgba(255,255,255,0.2)'>Allocations optimised to maximise Sharpe Ratio within your risk constraints.</div>", unsafe_allow_html=True)

        app_url = "https://portfolio-optimizer-uihgtnmomrcsl2ptkclwts.streamlit.app"
        st.markdown(f"<div style='margin-top:16px; font-size:11px; color:rgba(255,255,255,0.2)'>Share this tool:</div>", unsafe_allow_html=True)
        st.code(app_url, language=None)

    # ── CHART ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Historical View</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>2-Year Performance</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:rgba(255,255,255,0.3); margin-bottom:16px'>The indigo line shows your optimised portfolio. The white dashed line is the S&P 500 benchmark. Individual stocks shown faintly for reference.</div>", unsafe_allow_html=True)

    prices = result["prices"]
    norm = prices / prices.dropna().iloc[0] * 100
    fig_line = go.Figure()

    for col in norm.columns:
        fig_line.add_trace(go.Scatter(
            x=norm.index, y=norm[col],
            name=col, mode="lines",
            line=dict(width=1, color="rgba(255,255,255,0.12)"),
            showlegend=False,
            hovertemplate=f"<b>{col}</b><br>%{{y:.1f}}<extra></extra>"
        ))

    spy_data = result.get("spy_prices")
    if spy_data is not None and not spy_data.empty:
        spy_norm = spy_data / spy_data.dropna().iloc[0] * 100
        fig_line.add_trace(go.Scatter(
            x=spy_norm.index, y=spy_norm.values,
            name="S&P 500",
            mode="lines",
            line=dict(color="rgba(255,255,255,0.5)", width=2, dash="dash"),
            hovertemplate="<b>S&P 500</b><br>%{y:.1f}<extra></extra>"
        ))

    weight_series = weights_df.set_index("Stock")["Weight"]
    common = norm.columns.intersection(weight_series.index)
    portfolio_line = (norm[common] * weight_series[common]).sum(axis=1)
    fig_line.add_trace(go.Scatter(
        x=portfolio_line.index, y=portfolio_line,
        name="Your Portfolio",
        mode="lines",
        line=dict(color="#6366f1", width=3),
        hovertemplate="<b>Your Portfolio</b><br>%{y:.1f}<extra></extra>"
    ))

    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7,8,16,0.8)",
        font=dict(color="rgba(255,255,255,0.5)", family="DM Sans"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            title=dict(text="Date", font=dict(size=11)),
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.06)",
            title=dict(text="Normalised Value (Base = 100)", font=dict(size=11)),
            tickfont=dict(size=11)
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(t=16, b=16, l=16, r=16),
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ── NEXT STEPS ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>What Next</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your action plan</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='steps-grid'>
        <div class='step-card'>
            <div class='step-num'>01</div>
            <div class='step-text'>Screenshot or note your allocation percentages above</div>
        </div>
        <div class='step-card'>
            <div class='step-num'>02</div>
            <div class='step-text'>Open your brokerage (Freetrade, Trading 212, Hargreaves Lansdown)</div>
        </div>
        <div class='step-card'>
            <div class='step-num'>03</div>
            <div class='step-text'>Search each ticker and invest in the suggested proportions</div>
        </div>
        <div class='step-card'>
            <div class='step-num'>04</div>
            <div class='step-text'>Review and rebalance your portfolio every 6 to 12 months</div>
        </div>
        <div class='step-card'>
            <div class='step-num'>05</div>
            <div class='step-text'>Try adjusting your risk level or time horizon to explore other allocations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TRUST ──
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Transparency</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>How we built this</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='trust-grid'>
        <div class='trust-card'>
            <div class='trust-icon' style='background:rgba(99,102,241,0.1); color:#818cf8'>AI</div>
            <div class='trust-title'>AI Risk Profiling</div>
            <div class='trust-desc'>Google Gemini reads your goals and extracts your risk level, time horizon, preferred sectors, and maximum single-stock allocation.</div>
        </div>
        <div class='trust-card'>
            <div class='trust-icon' style='background:rgba(16,185,129,0.1); color:#10b981'>📊</div>
            <div class='trust-title'>Real Market Data</div>
            <div class='trust-desc'>Two years of adjusted close prices fetched live from Yahoo Finance for every stock in your portfolio.</div>
        </div>
        <div class='trust-card'>
            <div class='trust-icon' style='background:rgba(245,158,11,0.1); color:#f59e0b'>∑</div>
            <div class='trust-title'>Mathematical Optimisation</div>
            <div class='trust-desc'>Modern Portfolio Theory via SciPy SLSQP maximises your Sharpe Ratio — risk-adjusted return — within your constraints.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FEEDBACK ──
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Feedback</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Was this useful?</div>", unsafe_allow_html=True)
    fb1, fb2 = st.columns([1, 1])
    with fb1:
        if st.button("Yes, this was helpful"):
            st.success("Thank you — glad it was useful!")
    with fb2:
        if st.button("Something needs improving"):
            feedback = st.text_area("What could be better? We read every response.", key="fb_text", height=80)
            if feedback:
                st.success("Thank you — we will review this shortly.")

    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div class='footer'>
    <div class='footer-brand'>Folio AI</div>
    <div class='footer-links'>
        <a href='https://github.com/shriyajohari18/portfolio-optimizer' target='_blank'>GitHub</a>
        <a href='https://www.linkedin.com/in/shriya-johari-807736178/' target='_blank'>LinkedIn</a>
        <span style='color:rgba(255,255,255,0.1)'>Built by Shriya Johari</span>
    </div>
    <div class='footer-legal'>
        Educational purposes only. Not financial advice.<br>
        Data: Yahoo Finance · AI: Google Gemini · Maths: SciPy MPT
    </div>
</div>
""", unsafe_allow_html=True)
