import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AIzaSyC1kysyWYjUqZviz4QJIxIo1UKLwNEko5o")

def parse_risk_profile(user_description: str) -> dict:
    prompt = f"""
    A user described their investment goals: "{user_description}"
    
    Extract and return ONLY a JSON object with:
    - risk_level: integer 1-10 (1=very conservative, 10=very aggressive)
    - max_single_stock: float 0-1 (max allocation to one stock)
    - preferred_sectors: list of sectors they seem to prefer (or empty list)
    - time_horizon: "short" | "medium" | "long"
    - summary: one sentence explaining your interpretation
    
    Return ONLY valid JSON, no other text.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    
    raw = result["candidates"][0]["content"]["parts"][0]["text"]
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)
```

3. Press `Ctrl + S` to save

---

## Step 11: Create `optimizer.py`
*(No change — use the exact same code as before ✅)*

---

## Step 12: Create `app.py`
*(No change — use the exact same code as before ✅)*

---

## Step 13: Create `requirements.txt`
> **What changed:** We removed the `anthropic` library since we no longer need it.

1. Create `requirements.txt` and paste this:
```
streamlit
yfinance
numpy
scipy
plotly
pandas
python-dotenv
```

2. Press `Ctrl + S` to save

3. Now reinstall libraries to apply the change — go to Command Prompt and run:
```
pip install -r requirements.txt
```

---

# 🚀 Phase 5: Run the App

## Step 14: Launch It!
*(No change)*

1. Open Command Prompt
2. Make sure you see `(venv)` — if not, run:
```
cd Desktop\portfolio-optimizer
venv\Scripts\activate
```
3. Run the app:
```
streamlit run app.py
```
4. Browser opens at `http://localhost:8501` 🎉

---

# ☁️ Phase 6: Deploy Free Online

## Step 15: Push to GitHub
*(No change)*
```
echo venv/ > .gitignore
echo .env >> .gitignore
git init
git add .
git commit -m "Initial portfolio optimizer"
```

Then push to GitHub as described before.

---

## Step 16: Deploy on Streamlit Cloud
> **What changed:** You'll add your Gemini key instead of Anthropic key in the Secrets section.

1. Go to **share.streamlit.io** → Sign in with GitHub
2. Click **"New app"** → select your repo
3. Set main file to `app.py`
4. Click **"Advanced settings"** → under **Secrets** paste:
```
GEMINI_API_KEY = "AIzaSyC1kysyWYjUqZviz4QJIxIo1UKLwNEko5o"