#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

def getenv_or_exit(varname):
    v = os.getenv(varname)
    if not v:
        print(f"❌ ERROR: environment variable {varname!r} is not set or empty.", file=sys.stderr)
        sys.exit(1)
    return v

# 1) load & validate
PHONE_ID      = getenv_or_exit("PHONE_ID")
WABA_TOKEN    = getenv_or_exit("WABA_TOKEN")
USER_NUMBER   = getenv_or_exit("USER_NUMBER")
TEMPLATE_NAME = getenv_or_exit("TEMPLATE_NM")     # should be "hourly_trade_alert_us"
LANG_CODE     = os.getenv("LANG_CODE", "en_US")  # default to en_US if you like

# 2) build the request
url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {WABA_TOKEN}",
    "Content-Type": "application/json"
}

# example dynamic content
headline = "📰 Market News: Apple beats Q2 earnings"
trade    = "📈 Trade: AAPL — Jun 21 $175/$180 bull‐call‐spread"
note     = f"⏰ Note: Risk limited to $95, 72 % POP · {datetime.utcnow():%H:%M UTC}"

payload = {
    "messaging_product": "whatsapp",
    "to": USER_NUMBER,
    "type": "template",
    "template": {
        "name": TEMPLATE_NAME,
        "language": {"code": LANG_CODE},
        "components": [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": headline},
                {"type": "text", "text": trade},
                {"type": "text", "text": note}
            ]
        }]
    }
}

# 3) dump for debug
print("▶️ URL    :", url)
print("▶️ HEADERS:", json.dumps(headers, indent=2))
print("▶️ PAYLOAD:", json.dumps(payload, indent=2))

# 4) send
resp = requests.post(url, headers=headers, json=payload)
print(f"⏱ Status: {resp.status_code}", resp.text)

# 5) if error, extract error_data
if not resp.ok:
    try:
        err = resp.json().get("error", {})
        print("❌ API error.message   :", err.get("message"))
        print("❌ API error.code      :", err.get("code"))
        print("❌ API error.error_data:", json.dumps(err.get("error_data", {}), indent=2))
    except Exception as e:
        print("❌ Failed to parse error JSON:", e)
    sys.exit(1)

print("✅ Message sent successfully!")
