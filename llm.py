import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

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
