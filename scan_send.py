#!/usr/bin/env python3
"""
scan_send.py – very small proof‑of‑concept

• Looks up three required secrets from environment:
     PHONE_ID     – WhatsApp phone‑number ID that owns the template
     WABA_TOKEN   – Permanent system‑user token (Bearer)
     USER_NUMBER  – Destination phone number in E.164, e.g. 18178419493
• Uses two OPTIONAL env‑vars so you can change templates at will
     TEMPLATE_NS  – Message‑template namespace
     TEMPLATE_NM  – Template short name ( default = hourly_trade_alert )
"""

import os, json, datetime, requests, textwrap, sys

# ──▶ required secrets
try:
    PHONE_ID   = os.environ["PHONE_ID"]
    TOKEN      = os.environ["WABA_TOKEN"]
    TO         = os.environ["USER_NUMBER"]
except KeyError as e:
    sys.exit(f"❌ Missing environment variable: {e.args[0]}")

# ──▶ template info (namespace is required for Cloud API calls)
TEMPLATE_NS = os.getenv("TEMPLATE_NS", "")          # required on Cloud API
TEMPLATE_NM = os.getenv("TEMPLATE_NM", "hourly_trade_alert")
TEMPLATE_ID = f"{TEMPLATE_NS}:{TEMPLATE_NM}" if TEMPLATE_NS else TEMPLATE_NM

# ──▶ dummy payload data (replace with real scan output later)
headline = "📰 Market News: Apple beats Q2 earnings"
trade    = "💹 Trade: AAPL JUL 19 $175 / $180 bull‑call‑spread"
note     = "⏰ Note: Risk limited to $95, 72 % POP — manage accordingly."

# ──▶ build API body
body = {
    "messaging_product": "whatsapp",
    "to": TO,
    "type": "template",
    "template": {
        "name": TEMPLATE_ID,
        "language": { "code": "en_US" },
        "components": [{
            "type": "body",
            "parameters": [
                { "type": "text", "text": headline },
                { "type": "text", "text": trade    },
                { "type": "text", "text": note     }
            ]
        }]
    }
}

url  = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
auth = {"Authorization": f"Bearer {TOKEN}"}
hdrs = {**auth, "Content-Type": "application/json"}

# ──▶ send
resp = requests.post(url, headers=hdrs, data=json.dumps(body))
print("Status:", resp.status_code, resp.text[:400])
resp.raise_for_status()            # will raise if non‑200
print("✅ sent at", datetime.datetime.utcnow().isoformat(" ", "seconds"), "UTC")
