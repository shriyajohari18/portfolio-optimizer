import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import csv
import io
from datetime import datetime
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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500&display=swap');

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"],
section.main,.main .block-container,[data-testid="stMainBlockContainer"]{
  background:#07080f!important;font-family:'Inter',sans-serif!important;color:#fff!important
}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
#MainMenu,footer{display:none!important}
[data-testid="stSidebar"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important}
[data-testid="stColumn"]{background:transparent!important}

[data-testid="stExpander"],details,
[data-testid="stExpander"]>div,
[data-testid="stExpander"] details,
.streamlit-expanderHeader,.streamlit-expanderContent{
  background:#0c0d1a!important;background-color:#0c0d1a!important
}
[data-testid="stExpander"]{border:1px solid rgba(255,255,255,.07)!important;border-radius:10px!important;overflow:hidden!important}
[data-testid="stExpander"] summary p,[data-testid="stExpander"] p,
[data-testid="stExpander"] li{color:rgba(255,255,255,.45)!important;font-size:13px!important}
[data-testid="stExpander"] strong{color:rgba(255,255,255,.65)!important}
[data-testid="stExpander"] svg{fill:rgba(255,255,255,.25)!important}

.stTextArea>div,.stTextArea>div>div,.stTextInput>div,.stTextInput>div>div{background:transparent!important}
.stTextArea>div>div>textarea{
  background:#0c0d1a!important;border:1px solid rgba(255,255,255,.08)!important;
  border-radius:10px!important;color:#fff!important;font-family:'Inter',sans-serif!important;
  font-size:14px!important;font-weight:300!important;caret-color:#6366f1!important;resize:none!important
}
.stTextArea>div>div>textarea:focus{border-color:rgba(99,102,241,.5)!important;box-shadow:0 0 0 3px rgba(99,102,241,.08)!important;outline:none!important}
.stTextArea>div>div>textarea::placeholder{color:rgba(255,255,255,.18)!important}
.stTextInput>div>div>input{
  background:#0c0d1a!important;border:1px solid rgba(255,255,255,.08)!important;
  border-radius:10px!important;color:#fff!important;font-family:'Inter',sans-serif!important;
  font-size:13px!important;caret-color:#6366f1!important
}
.stTextInput>div>div>input:focus{border-color:rgba(99,102,241,.5)!important;box-shadow:0 0 0 3px rgba(99,102,241,.08)!important;outline:none!important}
.stTextInput>div>div>input::placeholder{color:rgba(255,255,255,.18)!important}
.stTextArea label p,.stTextInput label p{
  color:rgba(255,255,255,.25)!important;font-size:9px!important;font-weight:500!important;
  letter-spacing:.2em!important;text-transform:uppercase!important;margin-bottom:7px!important;font-family:'Inter',sans-serif!important
}

.stSelectbox>div>div{background:#0c0d1a!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;color:#fff!important}
.stSelectbox>div>div>div{color:#fff!important;font-size:13px!important}
.stSelectbox label p{color:rgba(255,255,255,.25)!important;font-size:9px!important;font-weight:500!important;letter-spacing:.2em!important;text-transform:uppercase!important;margin-bottom:7px!important}

.stButton>button{
  background:linear-gradient(135deg,#6366f1,#4f46e5)!important;color:#fff!important;
  border:none!important;border-radius:10px!important;padding:13px 28px!important;
  font-family:'Inter',sans-serif!important;font-size:14px!important;font-weight:500!important;
  width:100%!important;box-shadow:0 4px 20px rgba(99,102,241,.28)!important;transition:all .2s ease!important
}
.stButton>button:hover{background:linear-gradient(135deg,#818cf8,#6366f1)!important;transform:translateY(-1px)!important;box-shadow:0 6px 28px rgba(99,102,241,.42)!important}
.stButton>button:active{transform:translateY(0)!important}

.exbtn .stButton>button{
  background:#0c0d1a!important;color:rgba(255,255,255,.28)!important;
  border:1px solid rgba(255,255,255,.07)!important;border-radius:6px!important;
  padding:6px 12px!important;font-size:11px!important;font-weight:400!important;
  box-shadow:none!important
}
.exbtn .stButton>button:hover{background:rgba(99,102,241,.1)!important;border-color:rgba(99,102,241,.25)!important;color:#818cf8!important;transform:none!important;box-shadow:none!important}

.dlbtn .stButton>button{
  background:rgba(16,185,129,.08)!important;color:#10b981!important;
  border:1px solid rgba(16,185,129,.2)!important;border-radius:8px!important;
  padding:9px 18px!important;font-size:12.5px!important;font-weight:500!important;
  box-shadow:none!important
}
.dlbtn .stButton>button:hover{background:rgba(16,185,129,.15)!important;transform:none!important;box-shadow:none!important}

.histbtn .stButton>button{
  background:rgba(99,102,241,.07)!important;color:#818cf8!important;
  border:1px solid rgba(99,102,241,.18)!important;border-radius:7px!important;
  padding:7px 14px!important;font-size:11.5px!important;font-weight:400!important;box-shadow:none!important
}
.histbtn .stButton>button:hover{background:rgba(99,102,241,.14)!important;transform:none!important;box-shadow:none!important}

[data-testid="stAlert"]{background:rgba(245,158,11,.05)!important;border:1px solid rgba(245,158,11,.15)!important;border-radius:8px!important}
[data-testid="stAlert"] p{color:rgba(245,158,11,.8)!important;font-size:12.5px!important}
[data-testid="stInfo"]>div{background:rgba(99,102,241,.06)!important;border:1px solid rgba(99,102,241,.18)!important;border-radius:8px!important}
[data-testid="stSuccess"]>div{background:rgba(16,185,129,.06)!important;border:1px solid rgba(16,185,129,.18)!important;border-radius:8px!important}
[data-testid="stInfo"] p,[data-testid="stSuccess"] p{color:rgba(255,255,255,.6)!important;font-size:12.5px!important}

hr{border:none!important;border-top:1px solid rgba(255,255,255,.05)!important;margin:1.25rem 0!important}
.stSpinner>div{color:rgba(255,255,255,.3)!important}
[data-testid="stSpinner"]>div>div{border-top-color:#6366f1!important}
.stCodeBlock,[data-testid="stCode"]{background:#0c0d1a!important;border:1px solid rgba(255,255,255,.06)!important;border-radius:7px!important}
.stCodeBlock code{color:rgba(255,255,255,.35)!important;font-size:11px!important}

[data-testid="stDownloadButton"]>button{
  background:rgba(16,185,129,.08)!important;color:#10b981!important;
  border:1px solid rgba(16,185,129,.2)!important;border-radius:8px!important;
  padding:9px 18px!important;font-size:12.5px!important;font-weight:500!important;
  width:auto!important;box-shadow:none!important
}
[data-testid="stDownloadButton"]>button:hover{background:rgba(16,185,129,.15)!important;transform:none!important;box-shadow:none!important}
</style>
""", unsafe_allow_html=True)

def pad():
    _, c, _ = st.columns([.06, .88, .06])
    return c

# ── GLOBAL MARKETS ──
MARKETS = {
    "🇺🇸 United States": {"suffix": "", "label": "NYSE / NASDAQ — no suffix needed", "examples": "AAPL, MSFT, GOOGL, TSLA"},
    "🇬🇧 United Kingdom": {"suffix": ".L", "label": "London Stock Exchange — add .L", "examples": "HSBA.L, BP.L, SHEL.L, AZN.L"},
    "🇮🇳 India (NSE)": {"suffix": ".NS", "label": "National Stock Exchange — add .NS", "examples": "RELIANCE.NS, TCS.NS, INFY.NS"},
    "🇩🇪 Germany": {"suffix": ".DE", "label": "Frankfurt Exchange — add .DE", "examples": "SAP.DE, BMW.DE, BAYER.DE"},
    "🇫🇷 France": {"suffix": ".PA", "label": "Euronext Paris — add .PA", "examples": "MC.PA, TTE.PA, SAN.PA"},
    "🇯🇵 Japan": {"suffix": ".T", "label": "Tokyo Stock Exchange — add .T", "examples": "7203.T, 6758.T, 9984.T"},
    "🇭🇰 Hong Kong": {"suffix": ".HK", "label": "Hong Kong Exchange — add .HK", "examples": "0700.HK, 0005.HK, 0941.HK"},
    "🇦🇺 Australia": {"suffix": ".AX", "label": "ASX — add .AX", "examples": "CBA.AX, BHP.AX, CSL.AX"},
    "🌍 Mixed / Global": {"suffix": "", "label": "Enter tickers with their own suffixes", "examples": "AAPL, HSBA.L, RELIANCE.NS"},
}

SECTORS = {
    "tech":["AAPL","MSFT","GOOGL","NVDA","META"],
    "finance":["JPM","BAC","GS","V","MA"],
    "energy":["XOM","CVX","BP","SLB","COP"],
    "clean energy":["ENPH","NEE","SEDG","BEP","FSLR"],
    "healthcare":["JNJ","PFE","UNH","ABBV","MRK"],
    "consumer":["AMZN","WMT","PG","KO","MCD"],
    "real estate":["AMT","PLD","CCI","EQIX","SPG"],
    "default":["AAPL","MSFT","GOOGL","TSLA","NVDA","JPM","V","XOM"]
}

EXAMPLES = [
    ("Young & Ambitious","I am 24, just started my first job. I want aggressive growth over 30 years and love tech stocks. High risk is fine."),
    ("Mid-Career Planner","I am 38, stable income, two kids. I want moderate growth over 15 years with healthcare and consumer stocks."),
    ("Near Retirement","I am 58, retiring in 5 years. I need low volatility and capital preservation. Minimal risk please."),
    ("ESG Investor","I am 31, passionate about sustainability. Clean energy and ESG companies, medium risk, 20-year horizon.")
]

ERRS = {
    "429":"Our AI is taking a short break. Please wait 30 seconds and try again.",
    "403":"Authentication issue. Please try again shortly.",
    "404":"Could not reach our AI service. Please try again.",
    "400":"Could not understand the request. Please try rephrasing your goals.",
    "default":"Something went wrong. Please try again."
}

COLORS = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#84cc16","#f97316","#ec4899","#14b8a6"]

def tickers_from(text, sectors, suffix=""):
    t = set()
    tl = text.lower()
    for s in sectors:
        for k in SECTORS:
            if k in s.lower() or s.lower() in k:
                t.update(SECTORS[k])
    for k in SECTORS:
        if k in tl:
            t.update(SECTORS[k])
    if not t:
        t.update(SECTORS["default"])
    tickers = list(t)[:10]
    if suffix and suffix != "":
        tickers = [tick + suffix if not tick.endswith(suffix) else tick for tick in tickers]
    return tickers

def err_msg(e):
    m = str(e)
    for k,v in ERRS.items():
        if k in m: return v
    return ERRS["default"]

def r_info(r):
    c = "#10b981" if r>10 else "#f59e0b" if r>5 else "#ef4444"
    b = ("Above Market","bg") if r>10 else ("Near Market","ba") if r>5 else ("Below Market","br")
    d = abs(r-10)
    if r>15: o=f"Strong. {d:.1f}% above the S&P 500 historical average of ~10% per year."
    elif r>10: o=f"Good. {d:.1f}% above the S&P 500 historical average of ~10% per year."
    elif r>5: o=f"Moderate. {d:.1f}% below the S&P 500 average — consider a higher-risk allocation."
    else: o="Low. This portfolio may not keep pace with inflation long term."
    return c,b,o

def v_info(v):
    c = "#10b981" if v<15 else "#f59e0b" if v<25 else "#ef4444"
    b = ("Low Risk","bg") if v<15 else ("Moderate Risk","ba") if v<25 else ("High Risk","br")
    if v<10: o=f"Low. In a difficult year this portfolio could fall by roughly {v:.0f}%."
    elif v<20: o=f"Moderate. Expect price swings of around {v:.0f}% in either direction annually."
    elif v<30: o=f"High. Potential swings of up to {v:.0f}% per year — suits risk-tolerant investors."
    else: o=f"Very high. Potential swings of {v:.0f}%+ per year. Only for long-term aggressive investors."
    return c,b,o

def s_info(s):
    c = "#10b981" if s>=1 else "#f59e0b" if s>=.5 else "#ef4444"
    b = ("Excellent","bg") if s>=1 else ("Moderate","ba") if s>=.5 else ("Below Avg","br")
    if s>=2: o="Excellent. Every unit of risk is rewarded with 2+ units of return."
    elif s>=1: o="Good. You are being well-rewarded relative to the risk you are taking on."
    elif s>=.5: o="Moderate. Returns are reasonable but there may be better allocations."
    else: o="Below average. Consider diversifying into less correlated assets."
    return c,b,o

def badge(label, cls):
    col = {"bg":"rgba(16,185,129,.1);color:#10b981","ba":"rgba(245,158,11,.1);color:#f59e0b","br":"rgba(239,68,68,.1);color:#ef4444"}
    return f"<span style='display:inline-block;padding:3px 9px;border-radius:100px;font-size:10px;font-weight:500;margin-top:8px;background:{col[cls]}'>{label}</span>"

def T(t, size=9, color="rgba(255,255,255,.18)"):
    return f"<p style='font-size:{size}px;letter-spacing:.2em;text-transform:uppercase;color:{color};font-weight:500;margin:0 0 4px'>{t.upper()}</p>"

def H(t, size=18, mb=14):
    return f"<p style='font-family:Syne,sans-serif;font-size:{size}px;font-weight:800;color:#fff;letter-spacing:-.02em;margin:0 0 {mb}px'>{t}</p>"

def save_to_history(entry):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    st.session_state["history"].insert(0, entry)
    if len(st.session_state["history"]) > 10:
        st.session_state["history"] = st.session_state["history"][:10]

def make_csv(wdf, rv, vv, sv, tickers, goals):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Folio AI — Portfolio Export", datetime.now().strftime("%d %b %Y %H:%M")])
    w.writerow([])
    w.writerow(["Goals", goals])
    w.writerow(["Tickers", ", ".join(tickers)])
    w.writerow([])
    w.writerow(["Metric", "Value"])
    w.writerow(["Expected Annual Return", f"{rv}%"])
    w.writerow(["Expected Volatility", f"{vv}%"])
    w.writerow(["Sharpe Ratio", sv])
    w.writerow([])
    w.writerow(["Stock", "Allocation %", "Weight"])
    for _, row in wdf.iterrows():
        w.writerow([row["Stock"], f"{row['Pct']}%", round(row["Weight"], 4)])
    w.writerow([])
    w.writerow(["Note", "This is for educational purposes only. Not financial advice."])
    return buf.getvalue().encode()

# ══════════════════════════════════
# LOGO
# ══════════════════════════════════
LOGO_SVG = """
<svg width="100" height="28" viewBox="0 0 100 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="6" width="4" height="16" rx="2" fill="#6366f1" opacity="0.4"/>
  <rect x="7" y="2" width="4" height="24" rx="2" fill="#6366f1" opacity="0.65"/>
  <rect x="14" y="8" width="4" height="12" rx="2" fill="#818cf8"/>
  <rect x="21" y="4" width="4" height="20" rx="2" fill="#6366f1"/>
  <text x="34" y="20" font-family="Syne, sans-serif" font-weight="800" font-size="16" fill="white" letter-spacing="-0.5">Folio</text>
  <text x="72" y="20" font-family="Syne, sans-serif" font-weight="800" font-size="16" fill="#6366f1" letter-spacing="-0.5">AI</text>
</svg>
"""

# ══════════════════════════════════
# HEADER NAV
# ══════════════════════════════════
with pad():
    n1, n2, n3 = st.columns([1, 1, 1])
    with n1:
        st.markdown(f"<div style='padding:16px 0 8px'>{LOGO_SVG}</div>", unsafe_allow_html=True)
    with n2:
        st.markdown("""
        <div style='display:flex;align-items:center;justify-content:center;gap:24px;padding:20px 0 12px'>
          <a href='#' style='font-size:12px;color:rgba(255,255,255,.35);text-decoration:none'>How it works</a>
          <a href='#' style='font-size:12px;color:rgba(255,255,255,.35);text-decoration:none'>Global Markets</a>
          <a href='#' style='font-size:12px;color:rgba(255,255,255,.35);text-decoration:none'>History</a>
        </div>
        """, unsafe_allow_html=True)
    with n3:
        st.markdown("""
        <div style='display:flex;justify-content:flex-end;align-items:center;padding:20px 0 12px'>
          <a href='mailto:shriyajohari18@gmail.com' style='font-size:12px;color:#818cf8;text-decoration:none;padding:6px 14px;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);border-radius:100px'>
            ✉ Support
          </a>
        </div>
        """, unsafe_allow_html=True)

with pad():
    st.markdown("<div style='height:1px;background:rgba(255,255,255,.04);margin-bottom:0'></div>", unsafe_allow_html=True)

# ══════════════════════════════════
# HERO
# ══════════════════════════════════
with pad():
    st.markdown(f"""
    <div style='padding:52px 0 40px;border-bottom:1px solid rgba(255,255,255,.04)'>
      <p style='font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#6366f1;display:flex;align-items:center;gap:8px;margin:0 0 14px'>
        <span style='display:inline-block;width:20px;height:1px;background:#6366f1'></span>Smart Portfolio Optimisation — Global Markets
      </p>
      <h1 style='font-family:Syne,sans-serif;font-size:clamp(36px,4.5vw,64px);font-weight:800;line-height:1.0;letter-spacing:-.03em;color:#fff;margin:0 0 16px'>
        Build your<br><span style='background:linear-gradient(120deg,#818cf8,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>perfect portfolio.</span>
      </h1>
      <p style='font-size:14px;font-weight:300;color:rgba(255,255,255,.38);max-width:480px;line-height:1.75;margin:0 0 20px'>
        Tell us your goals in plain English. We use real market data from global exchanges and mathematical optimisation to build your ideal allocation — in under 60 seconds.
      </p>
      <span style='display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.18);border-radius:100px;font-size:11px;color:#818cf8'>
        <span style='font-size:6px'>◆</span> Unlike generic AI, Folio AI uses real historical market data and Modern Portfolio Theory — not guesswork
      </span>
      <div style='display:flex;gap:36px;margin-top:28px;padding-top:24px;border-top:1px solid rgba(255,255,255,.04)'>
        <div><p style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin:0'>MPT</p><p style='font-size:9px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.14em;margin:3px 0 0'>Optimisation</p></div>
        <div><p style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin:0'>2Y</p><p style='font-size:9px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.14em;margin:3px 0 0'>Historical Data</p></div>
        <div><p style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin:0'>8+</p><p style='font-size:9px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.14em;margin:3px 0 0'>Global Markets</p></div>
        <div><p style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin:0'>Free</p><p style='font-size:9px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.14em;margin:3px 0 0'>Always</p></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════
# DISCLAIMER + HOW IT WORKS
# ══════════════════════════════════
with pad():
    st.markdown("""
    <div style='padding:10px 14px;background:rgba(245,158,11,.05);border:1px solid rgba(245,158,11,.14);border-radius:8px;font-size:11.5px;color:rgba(245,158,11,.7);display:flex;gap:8px;line-height:1.55;margin:20px 0 12px'>
      <span style='flex-shrink:0'>⚠</span>
      <span>This tool is for <strong style='color:rgba(245,158,11,.9)'>educational purposes only</strong> and does not constitute financial advice. Past performance does not guarantee future results. Always consult a qualified financial adviser before investing.</span>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("How does Folio AI work?"):
        st.markdown("""
**Three steps:**
1. **Describe your goals** — your age, time horizon, risk appetite and any sectors you care about
2. **Select your market** — choose from US, UK, India, Germany, Japan and more
3. **We optimise** using Modern Portfolio Theory — the same framework used by professional fund managers

**Global market support:** US (NYSE/NASDAQ) · UK (LSE) · India (NSE) · Germany (Frankfurt) · France (Euronext) · Japan (TSE) · Hong Kong · Australia (ASX) · Mixed global portfolios

**What you receive:** Personalised risk profile · Optimised allocations · Plain English metric explanations · 2-year performance vs S&P 500 · Downloadable CSV for your investment app

**How we calculate this:** Real adjusted close prices from Yahoo Finance · Annualised returns and covariance matrix · Sharpe Ratio maximisation via SciPy · Google Gemini AI for goal understanding
        """)

with pad():
    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════
# HISTORY PANEL
# ══════════════════════════════════
history = st.session_state.get("history", [])
if history:
    with pad():
        st.markdown(T("Your Activity") + H("Past Portfolios", size=16, mb=12), unsafe_allow_html=True)
        h_cols = st.columns(min(len(history), 3), gap="small")
        for i, entry in enumerate(history[:3]):
            with h_cols[i]:
                st.markdown(f"""
                <div style='padding:14px;background:#0c0d1a;border:1px solid rgba(255,255,255,.06);border-radius:10px;cursor:pointer'>
                  <p style='font-size:9px;color:rgba(255,255,255,.2);letter-spacing:.1em;text-transform:uppercase;margin:0 0 5px'>{entry['date']}</p>
                  <p style='font-size:12.5px;color:rgba(255,255,255,.55);line-height:1.5;margin:0 0 8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden'>{entry['goals'][:80]}...</p>
                  <div style='display:flex;gap:8px;flex-wrap:wrap'>
                    <span style='font-size:10px;color:#10b981;background:rgba(16,185,129,.08);padding:2px 8px;border-radius:100px'>{entry["return"]}% return</span>
                    <span style='font-size:10px;color:#818cf8;background:rgba(99,102,241,.08);padding:2px 8px;border-radius:100px'>{entry["market"]}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div class='histbtn'>", unsafe_allow_html=True)
                if st.button(f"↗ Reload", key=f"hist_{i}"):
                    st.session_state["prefill"] = entry["goals"]
                    st.session_state["market_prefill"] = entry["market"]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════
# EXAMPLES
# ══════════════════════════════════
with pad():
    st.markdown(T("Quick Start") + H("Try an example"), unsafe_allow_html=True)
    ex_cards = "".join([
        f"""<div style='padding:12px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:8px'>
          <p style='font-size:8.5px;letter-spacing:.14em;text-transform:uppercase;color:#6366f1;margin:0 0 5px'>{l}</p>
          <p style='font-size:11px;color:rgba(255,255,255,.28);line-height:1.55;margin:0'>{t}</p>
        </div>"""
        for l, t in EXAMPLES
    ])
    st.markdown(f"<div style='display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-bottom:8px'>{ex_cards}</div>", unsafe_allow_html=True)
    st.markdown("<div class='exbtn'>", unsafe_allow_html=True)
    ecols = st.columns(4, gap="small")
    for i, (label, text) in enumerate(EXAMPLES):
        with ecols[i]:
            if st.button(f"↗ {label}", key=f"ex_{i}"):
                st.session_state["prefill"] = text
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with pad():
    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════
# MARKET SELECTOR + INPUTS
# ══════════════════════════════════
with pad():
    st.markdown(T("Step 1") + H("Select your market & describe your goals"), unsafe_allow_html=True)

    market_default = st.session_state.get("market_prefill", "🇺🇸 United States")
    market_keys = list(MARKETS.keys())
    market_idx = market_keys.index(market_default) if market_default in market_keys else 0
    selected_market = st.selectbox("Market", market_keys, index=market_idx, label_visibility="collapsed")
    market_info = MARKETS[selected_market]

    st.markdown(f"""
    <div style='padding:8px 14px;background:rgba(99,102,241,.05);border:1px solid rgba(99,102,241,.12);border-radius:7px;font-size:12px;color:rgba(255,255,255,.35);margin:6px 0 14px;display:flex;justify-content:space-between'>
      <span>{market_info['label']}</span>
      <span style='color:rgba(255,255,255,.2)'>e.g. {market_info['examples']}</span>
    </div>
    """, unsafe_allow_html=True)

    prefill = st.session_state.get("prefill", "")
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        user_input = st.text_area("Your investment goals", value=prefill,
            placeholder="E.g. I am 28, I want to build wealth for a house deposit in 5 years. I can handle moderate risk and I am interested in tech and clean energy.",
            height=130)
    with c2:
        ticker_input = st.text_input("Custom tickers (optional)", placeholder=market_info["examples"].split(",")[0].strip())
        st.markdown(f"<p style='font-size:11px;color:rgba(255,255,255,.18);margin-top:8px;line-height:1.65'>Leave blank — AI will suggest stocks for your selected market. {market_info['label']}.</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run = st.button("Optimise My Portfolio →")

# ══════════════════════════════════
# RESULTS
# ══════════════════════════════════
if run:
    if not user_input.strip():
        with pad():
            st.warning("Please describe your investment goals first.")
        st.stop()

    raw = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    suffix = market_info["suffix"]

    with pad():
        with st.spinner("Step 1 of 3 — Reading your goals and building your risk profile..."):
            try:
                profile = parse_risk_profile(user_input)
            except Exception as e:
                st.markdown(f"<div style='padding:12px 16px;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.16);border-radius:8px;font-size:13px;color:rgba(239,68,68,.75)'>{err_msg(e)}</div>", unsafe_allow_html=True)
                st.stop()

        tickers = raw if raw else tickers_from(user_input, profile.get("preferred_sectors", []), suffix)
        src = "your custom tickers" if raw else f"AI-selected for {selected_market}"
        st.info(f"Stocks selected ({src}): **{', '.join(tickers)}**")

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("Your Profile") + H("Risk Profile"), unsafe_allow_html=True)
        sec = ", ".join(profile.get("preferred_sectors", [])) or "Diversified"
        cards = "".join([
            f"""<div style='padding:18px 14px;background:#0c0d1a;border:1px solid rgba(255,255,255,.07);border-radius:10px;text-align:center;position:relative;overflow:hidden'>
              <div style='position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#6366f1,#10b981)'></div>
              <p style='font-family:Syne,sans-serif;font-size:{fs}px;font-weight:700;color:#fff;margin:0 0 4px;line-height:1.1'>{val}</p>
              <p style='font-size:9px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.12em;margin:0'>{lbl}</p>
            </div>"""
            for val, lbl, fs in [
                (f"{profile['risk_level']}<span style='font-size:13px;color:rgba(255,255,255,.2)'>/10</span>", "Risk Level", 24),
                (profile['time_horizon'].capitalize(), "Time Horizon", 24),
                (f"{int(profile['max_single_stock']*100)}<span style='font-size:13px;color:rgba(255,255,255,.2)'>%</span>", "Max Per Stock", 24),
                (f"<span style='font-size:14px'>{sec}</span>", "Sectors", 14),
            ]
        ])
        st.markdown(f"<div style='display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px'>{cards}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:13px 17px;background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.14);border-radius:8px;font-size:13.5px;color:rgba(255,255,255,.5);line-height:1.7'><strong style='color:#818cf8;font-weight:500'>AI says:</strong> {profile['summary']}</div>", unsafe_allow_html=True)

    with pad():
        with st.spinner("Step 2 of 3 — Fetching two years of live market data from global exchanges..."):
            pass
        with st.spinner("Step 3 of 3 — Running optimisation across thousands of portfolio combinations..."):
            try:
                result = optimize(tickers, profile['risk_level'], profile['max_single_stock'])
            except Exception as e:
                err = str(e)
                msg = "We could not find enough valid stock data. Please check your tickers and ensure they match the selected market format." if "2 valid" in err.lower() else f"Optimisation error: {err}."
                st.markdown(f"<div style='padding:12px 16px;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.16);border-radius:8px;font-size:13px;color:rgba(239,68,68,.75)'>{msg}</div>", unsafe_allow_html=True)
                st.stop()

    rv, vv, sv = result['expected_return'], result['volatility'], result['sharpe_ratio']
    rc, rb, ro = r_info(rv)
    vc, vb, vo = v_info(vv)
    sc, sb, so = s_info(sv)

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("Results") + H("Portfolio Performance"), unsafe_allow_html=True)
        pcards = "".join([
            f"""<div style='padding:22px 18px;background:#0c0d1a;border:1px solid rgba(255,255,255,.06);border-radius:12px'>
              <p style='font-family:Syne,sans-serif;font-size:40px;font-weight:800;line-height:1;letter-spacing:-.04em;color:{c};margin:0 0 3px'>{n}</p>
              <p style='font-size:9.5px;color:rgba(255,255,255,.22);text-transform:uppercase;letter-spacing:.14em;margin:0 0 11px'>{l}</p>
              <p style='font-size:12px;color:rgba(255,255,255,.42);line-height:1.65;padding-top:11px;border-top:1px solid rgba(255,255,255,.04);margin:0'>{d}</p>
              {badge(b[0],b[1])}
            </div>"""
            for c, n, l, d, b in [
                (rc, f"{rv}%", "Expected Annual Return", ro, rb),
                (vc, f"{vv}%", "Expected Volatility", vo, vb),
                (sc, str(sv), "Sharpe Ratio", so, sb),
            ]
        ])
        st.markdown(f"<div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px'>{pcards}</div>", unsafe_allow_html=True)

    wdf = pd.DataFrame(result["weights"].items(), columns=["Stock","Weight"])
    wdf["Pct"] = (wdf["Weight"]*100).round(2)
    wdf = wdf.sort_values("Weight", ascending=False).reset_index(drop=True)

    # Save to history
    save_to_history({
        "date": datetime.now().strftime("%d %b %Y"),
        "goals": user_input,
        "market": selected_market,
        "tickers": tickers,
        "return": rv,
        "volatility": vv,
        "sharpe": sv,
        "weights": wdf[["Stock","Pct"]].to_dict("records")
    })

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("Breakdown") + H("Portfolio Allocation"), unsafe_allow_html=True)
        l, r = st.columns([1, 1], gap="large")

        with l:
            fig = go.Figure(data=[go.Pie(
                labels=wdf["Stock"], values=wdf["Weight"], hole=0.64,
                marker=dict(colors=COLORS[:len(wdf)], line=dict(color="#07080f", width=3)),
                textinfo="label+percent", textfont=dict(size=11.5, color="white"),
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
            )])
            fig.add_annotation(text=f"<b>{len(wdf)}</b><br><span style='font-size:11px'>stocks</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="white", family="Syne"))
            fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=8,b=8,l=8,r=8),
                font=dict(color="white", family="Inter"))
            st.plotly_chart(fig, use_container_width=True)

        with r:
            rows = "".join([
                f"""<div style='display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.04)'>
                  <span style='font-size:13px;font-weight:500;color:#fff;width:64px;flex-shrink:0'>{row['Stock']}</span>
                  <div style='flex:1;height:2px;background:rgba(255,255,255,.06);border-radius:2px'>
                    <div style='height:2px;background:linear-gradient(90deg,#6366f1,#10b981);border-radius:2px;width:{min(row["Pct"],100)}%'></div>
                  </div>
                  <span style='font-family:Syne,sans-serif;font-size:13px;font-weight:700;color:#fff;width:40px;text-align:right;flex-shrink:0'>{row['Pct']}%</span>
                </div>"""
                for _, row in wdf.iterrows()
            ])
            st.markdown(f"<div style='padding-top:4px'>{rows}</div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:10.5px;color:rgba(255,255,255,.15);margin-top:12px'>Optimised to maximise Sharpe Ratio within your risk constraints.</p>", unsafe_allow_html=True)

            # ── DOWNLOADS ──
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown(T("Export", size=8) + "<p style='font-size:12px;color:rgba(255,255,255,.3);margin:0 0 8px'>Download for your investment app</p>", unsafe_allow_html=True)

            csv_data = make_csv(wdf, rv, vv, sv, tickers, user_input)
            d1, d2 = st.columns(2, gap="small")
            with d1:
                st.download_button(
                    label="↓ Download CSV",
                    data=csv_data,
                    file_name=f"folio_ai_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key="dl_csv"
                )
            with d2:
                json_data = json.dumps({
                    "generated": datetime.now().isoformat(),
                    "market": selected_market,
                    "goals": user_input,
                    "metrics": {"return": rv, "volatility": vv, "sharpe": sv},
                    "allocation": wdf[["Stock","Pct"]].to_dict("records")
                }, indent=2).encode()
                st.download_button(
                    label="↓ Download JSON",
                    data=json_data,
                    file_name=f"folio_ai_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    key="dl_json"
                )
            st.markdown("<p style='font-size:10.5px;color:rgba(255,255,255,.15);margin-top:8px;line-height:1.6'>CSV works with most brokerages and portfolio trackers. JSON for developers and custom tools.</p>", unsafe_allow_html=True)

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("Historical View") + H("2-Year Performance"), unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px;color:rgba(255,255,255,.22);margin-bottom:14px'>Indigo line = your portfolio · White dashed = S&P 500 benchmark · Individual stocks shown faintly for reference</p>", unsafe_allow_html=True)

        prices = result["prices"]
        norm = prices / prices.dropna().iloc[0] * 100
        fig2 = go.Figure()
        for col in norm.columns:
            fig2.add_trace(go.Scatter(x=norm.index, y=norm[col], name=col, mode="lines",
                line=dict(width=0.8, color="rgba(255,255,255,.07)"), showlegend=False,
                hovertemplate=f"<b>{col}</b>: %{{y:.1f}}<extra></extra>"))
        spy = result.get("spy_prices")
        if spy is not None and not spy.empty:
            sn = spy / spy.dropna().iloc[0] * 100
            fig2.add_trace(go.Scatter(x=sn.index, y=sn.values, name="S&P 500", mode="lines",
                line=dict(color="rgba(255,255,255,.38)", width=1.8, dash="dash"),
                hovertemplate="<b>S&P 500</b>: %{y:.1f}<extra></extra>"))
        ws = wdf.set_index("Stock")["Weight"]
        cm = norm.columns.intersection(ws.index)
        pl = (norm[cm] * ws[cm]).sum(axis=1)
        fig2.add_trace(go.Scatter(x=pl.index, y=pl, name="Your Portfolio", mode="lines",
            line=dict(color="#6366f1", width=2.5),
            hovertemplate="<b>Your Portfolio</b>: %{y:.1f}<extra></extra>"))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#09091c",
            font=dict(color="rgba(255,255,255,.3)", family="Inter"),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)", linecolor="rgba(255,255,255,.04)", title="Date", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(255,255,255,.03)", linecolor="rgba(255,255,255,.04)", title="Normalised Value (Base = 100)", tickfont=dict(size=10)),
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,.06)", borderwidth=1, font=dict(size=11)),
            margin=dict(t=8,b=8,l=4,r=4), hovermode="x unified"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("What Next") + H("Your action plan"), unsafe_allow_html=True)
        steps = "".join([
            f"""<div style='padding:14px 12px;background:#0c0d1a;border:1px solid rgba(255,255,255,.05);border-radius:8px'>
              <p style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:rgba(99,102,241,.2);margin:0 0 6px;line-height:1'>{n}</p>
              <p style='font-size:10.5px;color:rgba(255,255,255,.32);line-height:1.6;margin:0'>{t}</p>
            </div>"""
            for n,t in [
                ("01","Download your CSV and open it in your brokerage or portfolio tracker"),
                ("02","Open your brokerage — Freetrade, Trading 212, Robinhood, Zerodha, eToro"),
                ("03","Search each ticker and invest in the suggested proportions"),
                ("04","Review and rebalance your portfolio every 6 to 12 months"),
                ("05","Return to Folio AI and run a new optimisation as your goals change"),
            ]
        ])
        st.markdown(f"<div style='display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px'>{steps}</div>", unsafe_allow_html=True)

    with pad():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(T("Transparency") + H("How we built this"), unsafe_allow_html=True)
        tcards = "".join([
            f"""<div style='padding:18px 16px;background:#0c0d1a;border:1px solid rgba(255,255,255,.05);border-radius:10px'>
              <div style='width:30px;height:30px;border-radius:7px;background:{bg};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:{ic};margin-bottom:10px'>{ico}</div>
              <p style='font-family:Syne,sans-serif;font-size:13.5px;font-weight:700;color:#fff;margin:0 0 5px'>{h}</p>
              <p style='font-size:11.5px;color:rgba(255,255,255,.32);line-height:1.65;margin:0'>{d}</p>
            </div>"""
            for ico,bg,ic,h,d in [
                ("AI","rgba(99,102,241,.1)","#818cf8","AI Risk Profiling","Google Gemini reads your goals and extracts your risk level, time horizon, preferred sectors, and maximum single-stock allocation."),
                ("∑","rgba(16,185,129,.1)","#10b981","Global Market Data","Two years of adjusted close prices fetched live from Yahoo Finance for stocks across US, UK, India, EU, Japan, Australia and more."),
                ("◈","rgba(245,158,11,.1)","#f59e0b","Mathematical Optimisation","Modern Portfolio Theory via SciPy maximises your Sharpe Ratio — risk-adjusted return — within your personal risk constraints."),
            ]
        ])
        st.markdown(f"<div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px'>{tcards}</div>", unsafe_allow_html=True)

# ══════════════════════════════════
# FOOTER
# ══════════════════════════════════
with pad():
    st.markdown(f"""
    <hr>
    <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap;padding-bottom:36px'>
      <div>
        {LOGO_SVG}
        <p style='font-size:11.5px;color:rgba(255,255,255,.22);margin:10px 0 0;max-width:240px;line-height:1.65'>Smart portfolio optimisation for global markets. Built for everyone.</p>
      </div>
      <div>
        <p style='font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.18);margin:0 0 10px'>Links</p>
        <div style='display:flex;flex-direction:column;gap:7px'>
          <a href='https://github.com/shriyajohari18/portfolio-optimizer' target='_blank' style='font-size:12.5px;color:rgba(255,255,255,.3);text-decoration:none'>GitHub Repository</a>
          <a href='https://www.linkedin.com/in/shriya-johari-807736178/' target='_blank' style='font-size:12.5px;color:rgba(255,255,255,.3);text-decoration:none'>LinkedIn</a>
          <a href='mailto:shriyajohari18@gmail.com' style='font-size:12.5px;color:#818cf8;text-decoration:none'>shriyajohari18@gmail.com</a>
        </div>
      </div>
      <div>
        <p style='font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.18);margin:0 0 10px'>Support</p>
        <div style='display:flex;flex-direction:column;gap:7px'>
          <a href='mailto:shriyajohari18@gmail.com' style='font-size:12.5px;color:rgba(255,255,255,.3);text-decoration:none'>Report a bug</a>
          <a href='mailto:shriyajohari18@gmail.com' style='font-size:12.5px;color:rgba(255,255,255,.3);text-decoration:none'>Send feedback</a>
          <a href='mailto:shriyajohari18@gmail.com' style='font-size:12.5px;color:rgba(255,255,255,.3);text-decoration:none'>Request a feature</a>
        </div>
      </div>
      <div style='text-align:right'>
        <p style='font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.18);margin:0 0 10px'>Legal</p>
        <p style='font-size:11px;color:rgba(255,255,255,.15);line-height:1.7;margin:0'>Educational purposes only.<br>Not financial advice.<br>Data: Yahoo Finance<br>AI: Google Gemini<br>Built by Shriya Johari</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
