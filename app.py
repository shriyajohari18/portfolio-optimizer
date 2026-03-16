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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

/* ── BASE ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main, .main .block-container,
[data-testid="stMainBlockContainer"] {
    background-color: #080912 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #ffffff !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container,
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── COLUMN BACKGROUNDS ── */
[data-testid="stColumn"] {
    background: transparent !important;
}

/* ── ALL POSSIBLE EXPANDER SELECTORS ── */
[data-testid="stExpander"],
[data-testid="stExpander"] > div,
[data-testid="stExpander"] > div > div,
details, details > summary,
.streamlit-expanderHeader,
.streamlit-expanderContent {
    background-color: #0f1120 !important;
    background: #0f1120 !important;
    border-color: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.5) !important;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] strong {
    color: rgba(255,255,255,0.6) !important;
}
[data-testid="stExpander"] summary svg {
    fill: rgba(255,255,255,0.3) !important;
}

/* ── INPUTS ── */
.stTextArea > div > div > textarea {
    background-color: #0f1120 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    caret-color: #6366f1 !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
.stTextArea > div > div > textarea::placeholder { color: rgba(255,255,255,0.2) !important; }
.stTextArea > div { background: transparent !important; }

.stTextInput > div > div > input {
    background-color: #0f1120 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    caret-color: #6366f1 !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.2) !important; }
.stTextInput > div { background: transparent !important; }

.stTextArea label p, .stTextInput label p {
    color: rgba(255,255,255,0.3) !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    margin-bottom: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── MAIN BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(99,102,241,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── EXAMPLE BUTTONS — targeted by container class ── */
.ex-btn-container .stButton > button {
    background: #0f1120 !important;
    color: rgba(255,255,255,0.35) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
}
.ex-btn-container .stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #818cf8 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: rgba(245,158,11,0.07) !important;
    border: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p { color: rgba(245,158,11,0.85) !important; font-size: 13px !important; }
[data-testid="stInfo"] > div {
    background: rgba(99,102,241,0.07) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="stSuccess"] > div {
    background: rgba(16,185,129,0.07) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="stInfo"] p,
[data-testid="stSuccess"] p { color: rgba(255,255,255,0.65) !important; font-size: 13px !important; }

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.05) !important;
    margin: 1.5rem 0 !important;
}

/* ── SPINNER ── */
.stSpinner > div { color: rgba(255,255,255,0.35) !important; }
[data-testid="stSpinner"] > div > div { border-top-color: #6366f1 !important; }

/* ── CODE ── */
.stCodeBlock, [data-testid="stCode"] {
    background: #0f1120 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
}
.stCodeBlock code { color: rgba(255,255,255,0.4) !important; font-size: 11px !important; }

/* ── COMPONENT STYLES ── */
.eyebrow {
    font-size: 10px; font-weight: 500; letter-spacing: 0.22em;
    text-transform: uppercase; color: #6366f1; margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}
.eyebrow::before { content: ''; width: 24px; height: 1px; background: #6366f1; display: inline-block; }
.hero-h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(38px, 4.8vw, 68px);
    font-weight: 800; line-height: 1.02; color: #ffffff;
    margin-bottom: 20px; letter-spacing: -0.03em;
}
.hero-h1 .grad {
    background: linear-gradient(135deg, #818cf8 0%, #34d399 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-body {
    font-size: 15.5px; font-weight: 300; color: rgba(255,255,255,0.42);
    max-width: 500px; line-height: 1.75; margin-bottom: 24px;
}
.diff-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 15px; background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.22); border-radius: 100px;
    font-size: 11.5px; color: #818cf8; line-height: 1.4;
}
.diff-pill::before { content: '◆'; font-size: 6px; opacity: 0.7; }
.hero-stats {
    display: flex; gap: 44px; margin-top: 36px;
    padding-top: 32px; border-top: 1px solid rgba(255,255,255,0.05);
}
.stat-val { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 700; color: #fff; line-height: 1; }
.stat-lbl { font-size: 9.5px; color: rgba(255,255,255,0.25); margin-top: 5px; text-transform: uppercase; letter-spacing: 0.14em; }

.disc {
    padding: 12px 16px; background: rgba(245,158,11,0.05);
    border: 1px solid rgba(245,158,11,0.18); border-radius: 10px;
    font-size: 12.5px; color: rgba(245,158,11,0.7);
    display: flex; gap: 10px; align-items: flex-start; line-height: 1.6;
}

.sec-lbl {
    font-size: 9.5px; font-weight: 500; letter-spacing: 0.24em;
    text-transform: uppercase; color: rgba(255,255,255,0.18); margin-bottom: 4px;
}
.sec-h2 {
    font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700;
    color: #ffffff; margin-bottom: 18px; letter-spacing: -0.02em;
}

.ex-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 10px; }
.ex-card {
    padding: 14px 13px; background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;
}
.ex-tag { font-size: 9px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #6366f1; margin-bottom: 6px; }
.ex-body { font-size: 12px; color: rgba(255,255,255,0.32); line-height: 1.55; }

.profile-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px; }
.p-card {
    padding: 18px 14px; background: #0d0f1e;
    border: 1px solid rgba(255,255,255,0.07); border-radius: 12px;
    text-align: center; position: relative; overflow: hidden;
}
.p-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6366f1, #10b981);
}
.p-val { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 700; color: #fff; line-height: 1.1; margin-bottom: 5px; }
.p-lbl { font-size: 9.5px; color: rgba(255,255,255,0.25); text-transform: uppercase; letter-spacing: 0.12em; }

.interp {
    padding: 14px 18px; background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.15); border-radius: 10px;
    font-size: 13.5px; color: rgba(255,255,255,0.52); line-height: 1.7; margin-top: 14px;
}
.interp b { color: #818cf8; font-weight: 500; }

.perf-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.perf-card { padding: 24px 20px; background: #0d0f1e; border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; }
.perf-num { font-family: 'Syne', sans-serif; font-size: 42px; font-weight: 800; line-height: 1; letter-spacing: -0.04em; margin-bottom: 3px; }
.perf-lbl { font-size: 10px; color: rgba(255,255,255,0.25); text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 12px; }
.perf-out { font-size: 12.5px; color: rgba(255,255,255,0.45); line-height: 1.65; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); }
.badge { display: inline-block; padding: 3px 10px; border-radius: 100px; font-size: 10.5px; font-weight: 500; margin-top: 10px; }
.b-green { background: rgba(16,185,129,0.1); color: #10b981; }
.b-amber { background: rgba(245,158,11,0.1); color: #f59e0b; }
.b-red   { background: rgba(239,68,68,0.1);  color: #ef4444; }

.alloc-t { width: 100%; border-collapse: collapse; }
.alloc-t tr { border-bottom: 1px solid rgba(255,255,255,0.04); }
.alloc-t tr:last-child { border-bottom: none; }
.alloc-t td { padding: 11px 0; font-size: 13.5px; }
.alloc-t .ticker { font-weight: 500; color: #fff; }
.alloc-t .pct { font-family: 'Syne', sans-serif; font-weight: 600; color: #fff; text-align: right; white-space: nowrap; }
.bar-bg { width: 100%; height: 2px; background: rgba(255,255,255,0.06); border-radius: 2px; margin-top: 5px; }
.bar-fg { height: 2px; background: linear-gradient(90deg, #6366f1, #10b981); border-radius: 2px; }

.steps-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.step { padding: 16px 13px; background: #0d0f1e; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; }
.step-n { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: rgba(99,102,241,0.22); margin-bottom: 7px; line-height: 1; }
.step-t { font-size: 11.5px; color: rgba(255,255,255,0.38); line-height: 1.6; }

.trust-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.trust-c { padding: 18px 16px; background: #0d0f1e; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; }
.trust-ico { width: 30px; height: 30px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; margin-bottom: 10px; }
.trust-h { font-family: 'Syne', sans-serif; font-size: 13.5px; font-weight: 600; color: #fff; margin-bottom: 5px; }
.trust-d { font-size: 12px; color: rgba(255,255,255,0.35); line-height: 1.65; }

.err { padding: 13px 16px; background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.18); border-radius: 10px; font-size: 13px; color: rgba(239,68,68,0.75); }

.footer-row {
    display: flex; justify-content: space-between; align-items: center;
    gap: 20px; flex-wrap: wrap; padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.ft-brand { font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 800; color: rgba(255,255,255,0.1); }
.ft-links { display: flex; gap: 18px; align-items: center; }
.ft-links a { font-size: 12px; color: rgba(255,255,255,0.28); text-decoration: none; transition: color 0.2s; }
.ft-links a:hover { color: #818cf8; }
.ft-sep { color: rgba(255,255,255,0.1); font-size: 12px; }
.ft-legal { font-size: 10.5px; color: rgba(255,255,255,0.12); text-align: right; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

PAD = 0.07

def padded():
    _, col, _ = st.columns([PAD, 1 - 2*PAD, PAD])
    return col

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
    ("Young & Ambitious",  "I am 24, just started my first job. I want aggressive growth over 30 years and love tech stocks. High risk is fine."),
    ("Mid-Career Planner", "I am 38, stable income, two kids. I want moderate growth over 15 years with healthcare and consumer stocks."),
    ("Near Retirement",    "I am 58, retiring in 5 years. I need low volatility and capital preservation. Minimal risk please."),
    ("ESG Investor",       "I am 31, passionate about sustainability. Clean energy and ESG companies, medium risk, 20-year horizon.")
]
ERROR_MESSAGES = {
    "429": "Our AI is taking a short break due to high demand. Please wait 30 seconds and try again.",
    "403": "There was an authentication issue. Please try again shortly.",
    "404": "We could not reach our AI service. Please try again in a moment.",
    "400": "We had trouble understanding your request. Please try rephrasing your goals.",
    "default": "Something went wrong. Please try again — if this persists, try refreshing the page."
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

def return_info(r):
    col = "#10b981" if r > 10 else "#f59e0b" if r > 5 else "#ef4444"
    badge = ("Above Market", "b-green") if r > 10 else ("Near Market", "b-amber") if r > 5 else ("Below Market", "b-red")
    diff = abs(r - 10)
    if r > 15: out = f"Strong. {diff:.1f}% above the S&P 500 historical average of ~10% per year."
    elif r > 10: out = f"Good. {diff:.1f}% above the S&P 500 historical average of ~10% per year."
    elif r > 5: out = f"Moderate. {diff:.1f}% below the S&P 500 average — consider a higher-risk allocation."
    else: out = "Low. This portfolio may not keep pace with inflation long term."
    return col, badge, out

def vol_info(v):
    col = "#10b981" if v < 15 else "#f59e0b" if v < 25 else "#ef4444"
    badge = ("Low Risk", "b-green") if v < 15 else ("Moderate Risk", "b-amber") if v < 25 else ("High Risk", "b-red")
    if v < 10: out = f"Low. In a difficult year, this portfolio could fall by roughly {v:.0f}%."
    elif v < 20: out = f"Moderate. Expect price swings of around {v:.0f}% in either direction annually."
    elif v < 30: out = f"High. Potential swings of up to {v:.0f}% per year — suits risk-tolerant investors."
    else: out = f"Very high. Potential swings of {v:.0f}%+ per year. Only suitable for long-term aggressive investors."
    return col, badge, out

def sharpe_info(s):
    col = "#10b981" if s >= 1 else "#f59e0b" if s >= 0.5 else "#ef4444"
    badge = ("Excellent", "b-green") if s >= 1 else ("Moderate", "b-amber") if s >= 0.5 else ("Below Average", "b-red")
    if s >= 2: out = "Excellent. Every unit of risk is rewarded with 2+ units of return."
    elif s >= 1: out = "Good. You are being well-rewarded relative to the risk you are taking on."
    elif s >= 0.5: out = "Moderate. Returns are reasonable but there may be better allocations."
    else: out = "Below average. Consider diversifying into less correlated assets."
    return col, badge, out

# ═══════════════════════════════════════
# HERO
# ═══════════════════════════════════════
st.markdown("""
<style>
.hero-strip {
    background: linear-gradient(175deg, #0e1128 0%, #080912 100%);
    border-bottom: 1px solid rgba(255,255,255,0.04);
    padding: 60px 0 48px;
    position: relative; overflow: hidden;
}
.glow1 { position:absolute; top:-180px; right:0; width:560px; height:560px; background:radial-gradient(circle,rgba(99,102,241,0.13) 0%,transparent 65%); pointer-events:none; }
.glow2 { position:absolute; bottom:-80px; left:28%; width:440px; height:440px; background:radial-gradient(circle,rgba(16,185,129,0.06) 0%,transparent 65%); pointer-events:none; }
</style>
<div class="hero-strip">
  <div class="glow1"></div>
  <div class="glow2"></div>
</div>
""", unsafe_allow_html=True)

with padded():
    st.markdown("""
    <div class='eyebrow'>AI-Powered Portfolio Optimisation</div>
    <div class='hero-h1'>Build your<br><span class='grad'>perfect portfolio.</span></div>
    <div class='hero-body'>Tell us your goals in plain English. We use real market data and mathematical optimisation to build your ideal investment allocation — in under 60 seconds.</div>
    <div class='diff-pill'>Unlike generic AI chatbots, Folio AI uses real historical market data and Modern Portfolio Theory — not guesswork</div>
    <div class='hero-stats'>
      <div><div class='stat-val'>MPT</div><div class='stat-lbl'>Optimisation Engine</div></div>
      <div><div class='stat-val'>2Y</div><div class='stat-lbl'>Historical Data</div></div>
      <div><div class='stat-val'>Live</div><div class='stat-lbl'>Market Prices</div></div>
      <div><div class='stat-val'>Free</div><div class='stat-lbl'>Always</div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── DISCLAIMER ──
with padded():
    st.markdown("""
    <div class='disc'>
      <span style='margin-top:1px;flex-shrink:0'>⚠</span>
      <span>This tool is for <strong>educational purposes only</strong> and does not constitute financial advice. Past performance does not guarantee future results. Always consult a qualified financial adviser before investing.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── HOW IT WORKS ──
with padded():
    with st.expander("How does Folio AI work?"):
        st.markdown("""
**Three steps:**
1. **Describe your goals** — your age, time horizon, risk appetite and any sectors you care about
2. **We select stocks** automatically, or enter your own tickers
3. **We optimise** using Modern Portfolio Theory — the same framework used by professional fund managers

**What you receive:** Personalised risk profile · Optimised allocations · Plain English metric explanations · 2-year performance vs S&P 500

**How we calculate this:** Real adjusted close prices from Yahoo Finance · Annualised returns and covariance matrix · Sharpe Ratio maximisation via SciPy · Google Gemini AI for goal understanding

**For Indian stocks:** Add .NS to any NSE ticker — e.g. RELIANCE.NS, TCS.NS, HDFCBANK.NS
        """)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

with padded():
    st.markdown("<hr>", unsafe_allow_html=True)

# ── EXAMPLES ──
with padded():
    st.markdown("<div class='sec-lbl'>Quick Start</div><div class='sec-h2'>Try an example</div>", unsafe_allow_html=True)
    st.markdown("<div class='ex-grid'>" + "".join([
        f"<div class='ex-card'><div class='ex-tag'>{label}</div><div class='ex-body'>{text}</div></div>"
        for label, text in EXAMPLES
    ]) + "</div>", unsafe_allow_html=True)

    st.markdown("<div class='ex-btn-container'>", unsafe_allow_html=True)
    ex_cols = st.columns(4, gap="small")
    for i, (label, text) in enumerate(EXAMPLES):
        with ex_cols[i]:
            if st.button(f"↗ {label}", key=f"ex_{i}"):
                st.session_state["prefill"] = text
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with padded():
    st.markdown("<hr>", unsafe_allow_html=True)

# ── INPUTS ──
with padded():
    st.markdown("<div class='sec-lbl'>Step 1</div><div class='sec-h2'>Describe your goals</div>", unsafe_allow_html=True)
    prefill = st.session_state.get("prefill", "")
    col1, col2 = st.columns([2, 1], gap="large")
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
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.2);margin-top:8px;line-height:1.7'>Leave blank — AI will suggest stocks based on your goals. Add .NS for Indian NSE stocks.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    run = st.button("Optimise My Portfolio →")

# ═══════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════
if run:
    if not user_input.strip():
        with padded():
            st.warning("Please describe your investment goals first.")
        st.stop()

    tickers_raw = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    with padded():
        with st.spinner("Step 1 of 3 — Reading your goals and building your risk profile..."):
            try:
                profile = parse_risk_profile(user_input)
            except Exception as e:
                st.markdown(f"<div class='err'>{friendly_error(e)}</div>", unsafe_allow_html=True)
                st.stop()
        tickers = tickers_raw if tickers_raw else suggest_tickers(user_input, profile.get("preferred_sectors", []))
        source = "your custom tickers" if tickers_raw else "AI-selected based on your goals"
        st.info(f"Stocks selected ({source}): **{', '.join(tickers)}**")

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>Your Profile</div><div class='sec-h2'>Risk Profile</div>", unsafe_allow_html=True)
        sectors_display = ", ".join(profile.get("preferred_sectors", [])) or "Diversified"
        st.markdown(f"""
        <div class='profile-row'>
          <div class='p-card'><div class='p-val'>{profile['risk_level']}<span style='font-size:13px;color:rgba(255,255,255,0.22)'>/10</span></div><div class='p-lbl'>Risk Level</div></div>
          <div class='p-card'><div class='p-val'>{profile['time_horizon'].capitalize()}</div><div class='p-lbl'>Time Horizon</div></div>
          <div class='p-card'><div class='p-val'>{int(profile['max_single_stock']*100)}<span style='font-size:13px;color:rgba(255,255,255,0.22)'>%</span></div><div class='p-lbl'>Max Per Stock</div></div>
          <div class='p-card'><div class='p-val' style='font-size:15px'>{sectors_display}</div><div class='p-lbl'>Sectors</div></div>
        </div>
        <div class='interp'><b>AI says:</b> {profile['summary']}</div>
        """, unsafe_allow_html=True)

    with padded():
        with st.spinner("Step 2 of 3 — Fetching two years of live market data for all stocks..."):
            pass
        with st.spinner("Step 3 of 3 — Running optimisation across thousands of portfolio combinations..."):
            try:
                result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
            except Exception as e:
                err = str(e)
                if "2 valid" in err.lower() or "valid ticker" in err.lower():
                    msg = "We could not find enough valid stock data. Please check your tickers. Indian stocks need .NS (e.g. RELIANCE.NS)."
                else:
                    msg = f"Optimisation error: {err}. Please check your tickers and try again."
                st.markdown(f"<div class='err'>{msg}</div>", unsafe_allow_html=True)
                st.stop()

    r, v, s = result['expected_return'], result['volatility'], result['sharpe_ratio']
    rc, rb, ro = return_info(r)
    vc, vb, vo = vol_info(v)
    sc, sb, so = sharpe_info(s)

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>Results</div><div class='sec-h2'>Portfolio Performance</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='perf-row'>
          <div class='perf-card'><div class='perf-num' style='color:{rc}'>{r}%</div><div class='perf-lbl'>Expected Annual Return</div><div class='perf-out'>{ro}</div><div class='badge {rb[1]}'>{rb[0]}</div></div>
          <div class='perf-card'><div class='perf-num' style='color:{vc}'>{v}%</div><div class='perf-lbl'>Expected Volatility</div><div class='perf-out'>{vo}</div><div class='badge {vb[1]}'>{vb[0]}</div></div>
          <div class='perf-card'><div class='perf-num' style='color:{sc}'>{s}</div><div class='perf-lbl'>Sharpe Ratio</div><div class='perf-out'>{so}</div><div class='badge {sb[1]}'>{sb[0]}</div></div>
        </div>
        """, unsafe_allow_html=True)

    weights_df = pd.DataFrame(result["weights"].items(), columns=["Stock", "Weight"])
    weights_df["Allocation %"] = (weights_df["Weight"] * 100).round(2)
    weights_df = weights_df.sort_values("Weight", ascending=False).reset_index(drop=True)

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>Breakdown</div><div class='sec-h2'>Portfolio Allocation</div>", unsafe_allow_html=True)
        colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#84cc16","#f97316","#ec4899","#14b8a6"]
        left, right = st.columns([1, 1], gap="large")

        with left:
            fig_pie = go.Figure(data=[go.Pie(
                labels=weights_df["Stock"], values=weights_df["Weight"], hole=0.62,
                marker=dict(colors=colors[:len(weights_df)], line=dict(color='#080912', width=3)),
                textinfo="label+percent", textfont=dict(size=12, color="white"),
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
            )])
            fig_pie.add_annotation(text=f"<b>{len(weights_df)}</b><br>stocks", x=0.5, y=0.5, showarrow=False, font=dict(size=19, color="white", family="Syne"))
            fig_pie.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=8,b=8,l=8,r=8), font=dict(color="white", family="DM Sans"))
            st.plotly_chart(fig_pie, use_container_width=True)

        with right:
            rows = "".join([f"""<tr>
              <td class='ticker'>{row['Stock']}</td>
              <td style='padding:11px 12px'><div class='bar-bg'><div class='bar-fg' style='width:{min(row["Allocation %"],100)}%'></div></div></td>
              <td class='pct'>{row['Allocation %']}%</td>
            </tr>""" for _, row in weights_df.iterrows()])
            st.markdown(f"<table class='alloc-t'>{rows}</table>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:12px;font-size:11px;color:rgba(255,255,255,0.15)'>Allocations optimised to maximise Sharpe Ratio within your risk constraints.</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:16px;font-size:11px;color:rgba(255,255,255,0.18);margin-bottom:5px'>Share this tool:</div>", unsafe_allow_html=True)
            st.code("https://portfolio-optimizer-uihgtnmomrcsl2ptkclwts.streamlit.app", language=None)

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>Historical View</div><div class='sec-h2'>2-Year Performance</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12.5px;color:rgba(255,255,255,0.25);margin-bottom:14px'>The indigo line is your optimised portfolio. The white dashed line is the S&P 500 benchmark.</div>", unsafe_allow_html=True)

        prices = result["prices"]
        norm = prices / prices.dropna().iloc[0] * 100
        fig = go.Figure()
        for col in norm.columns:
            fig.add_trace(go.Scatter(x=norm.index, y=norm[col], name=col, mode="lines",
                line=dict(width=1, color="rgba(255,255,255,0.08)"), showlegend=False,
                hovertemplate=f"<b>{col}</b>: %{{y:.1f}}<extra></extra>"))
        spy_data = result.get("spy_prices")
        if spy_data is not None and not spy_data.empty:
            spy_norm = spy_data / spy_data.dropna().iloc[0] * 100
            fig.add_trace(go.Scatter(x=spy_norm.index, y=spy_norm.values, name="S&P 500", mode="lines",
                line=dict(color="rgba(255,255,255,0.4)", width=2, dash="dash"),
                hovertemplate="<b>S&P 500</b>: %{y:.1f}<extra></extra>"))
        weight_series = weights_df.set_index("Stock")["Weight"]
        common = norm.columns.intersection(weight_series.index)
        port_line = (norm[common] * weight_series[common]).sum(axis=1)
        fig.add_trace(go.Scatter(x=port_line.index, y=port_line, name="Your Portfolio", mode="lines",
            line=dict(color="#6366f1", width=2.5),
            hovertemplate="<b>Your Portfolio</b>: %{y:.1f}<extra></extra>"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#09091a",
            font=dict(color="rgba(255,255,255,0.35)", family="DM Sans"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.05)", title="Date", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.03)", linecolor="rgba(255,255,255,0.05)", title="Normalised Value (Base = 100)", tickfont=dict(size=10)),
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.07)", borderwidth=1, font=dict(size=11)),
            margin=dict(t=8, b=8, l=4, r=4), hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>What Next</div><div class='sec-h2'>Your action plan</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='steps-row'>
          <div class='step'><div class='step-n'>01</div><div class='step-t'>Screenshot or note your allocation percentages above</div></div>
          <div class='step'><div class='step-n'>02</div><div class='step-t'>Open your brokerage — Freetrade, Trading 212 or Hargreaves Lansdown</div></div>
          <div class='step'><div class='step-n'>03</div><div class='step-t'>Search each ticker and invest in the suggested proportions</div></div>
          <div class='step'><div class='step-n'>04</div><div class='step-t'>Review and rebalance your portfolio every 6 to 12 months</div></div>
          <div class='step'><div class='step-n'>05</div><div class='step-t'>Try a different risk level or time horizon to explore other allocations</div></div>
        </div>
        """, unsafe_allow_html=True)

    with padded():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='sec-lbl'>Transparency</div><div class='sec-h2'>How we built this</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='trust-row'>
          <div class='trust-c'><div class='trust-ico' style='background:rgba(99,102,241,0.1);color:#818cf8'>AI</div><div class='trust-h'>AI Risk Profiling</div><div class='trust-d'>Google Gemini reads your goals and extracts your risk level, time horizon, preferred sectors, and maximum single-stock allocation.</div></div>
          <div class='trust-c'><div class='trust-ico' style='background:rgba(16,185,129,0.1);color:#10b981'>∑</div><div class='trust-h'>Real Market Data</div><div class='trust-d'>Two years of adjusted close prices fetched live from Yahoo Finance for every stock in your portfolio.</div></div>
          <div class='trust-c'><div class='trust-ico' style='background:rgba(245,158,11,0.1);color:#f59e0b'>◈</div><div class='trust-h'>Mathematical Optimisation</div><div class='trust-d'>Modern Portfolio Theory via SciPy maximises your Sharpe Ratio — risk-adjusted return — within your personal constraints.</div></div>
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ──
with padded():
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class='footer-row'>
      <div class='ft-brand'>Folio AI</div>
      <div class='ft-links'>
        <a href='https://github.com/shriyajohari18/portfolio-optimizer' target='_blank'>GitHub</a>
        <span class='ft-sep'>·</span>
        <a href='https://www.linkedin.com/in/shriya-johari-807736178/' target='_blank'>LinkedIn</a>
        <span class='ft-sep'>·</span>
        <span style='color:rgba(255,255,255,0.16);font-size:12px'>Built by Shriya Johari</span>
      </div>
      <div class='ft-legal'>Educational purposes only. Not financial advice.<br>Data: Yahoo Finance &nbsp;·&nbsp; AI: Google Gemini &nbsp;·&nbsp; Maths: SciPy MPT</div>
    </div>
    <div style='height:32px'></div>
    """, unsafe_allow_html=True)
