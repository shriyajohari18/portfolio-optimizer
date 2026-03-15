import json
import os
import time
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def parse_risk_profile(user_description: str) -> dict:
    prompt = (
        "A user described their investment goals: \"" + user_description + "\"\n\n"
        "Extract and return ONLY a JSON object with these exact keys:\n"
        "- risk_level: integer 1-10 (1=very conservative, 10=very aggressive)\n"
        "- max_single_stock: float 0-1 (max allocation to one stock)\n"
        "- preferred_sectors: list of sectors they seem to prefer (or empty list)\n"
        "- time_horizon: short or medium or long\n"
        "- summary: one sentence explaining your interpretation\n\n"
        "Return ONLY valid JSON, no other text, no markdown, no backticks."
    )

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + API_KEY

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    for attempt in range(3):
        try:
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
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(15)
            else:
                raise e
