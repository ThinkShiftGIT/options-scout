#!/usr/bin/env python3
# scan_send.py — sends a WhatsApp template message via Business Cloud API

import os
import sys
import requests

# ── load configuration from GitHub repo secrets & variables ───────────────
PHONE_ID      = os.getenv("PHONE_ID")        # repo secret: your phone number ID
TOKEN         = os.getenv("WABA_TOKEN")      # repo secret: your WhatsApp API token
TO            = os.getenv("USER_NUMBER")     # repo secret: destination phone number
TEMPLATE_NAME = os.getenv("TEMPLATE_NM")     # repo variable: hourly_trade_alert_us
LANG_CODE     = os.getenv("LANG_CODE")       # repo variable: en_US

required = {
    "PHONE_ID": PHONE_ID,
    "WABA_TOKEN": TOKEN,
    "USER_NUMBER": TO,
    "TEMPLATE_NM": TEMPLATE_NAME,
    "LANG_CODE": LANG_CODE,
}
missing = [k for k,v in required.items() if not v]
if missing:
    print(f"❌ Missing required env vars: {missing}", file=sys.stderr)
    sys.exit(1)

# ── build your dynamic parameters ────────────────────────────────────────────
headline = "📰 Market News: Apple beats Q2 earnings"
trade    = "💡 Trade: AAPL – Jun 21 $175/$180 bull-call-spread"
note     = "⏰ Note: Risk limited to $95, 72 % POP"

# ── assemble the API request ────────────────────────────────────────────────
url = f"https://graph.facebook.com/v16.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
body = {
    "messaging_product": "whatsapp",
    "to": TO,
    "type": "template",
    "template": {
        "name": TEMPLATE_NAME,
        "language": {"code": LANG_CODE},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": headline},
                    {"type": "text", "text": trade},
                    {"type": "text", "text": note}
                ]
            }
        ]
    }
}

# ── fire off the request & show result ─────────────────────────────────────
resp = requests.post(url, headers=headers, json=body)
print(f"Status: {resp.status_code}  Response: {resp.text}")
if not resp.ok:
    sys.exit(1)
