#!/usr/bin/env python3
"""
scan_send.py – WhatsApp Cloud API Alert Sender with debug prints

This script reads configuration from environment variables, builds a
templated WhatsApp message payload, dumps the full request for debugging,
and sends it via the WhatsApp Business Cloud API.

Required environment variables (set under GitHub → Settings → Secrets & Variables → Actions):
  PHONE_ID      – WhatsApp phone-number ID (from API Setup)
  WABA_TOKEN    – Permanent system-user access token (Never expires)
  USER_NUMBER   – Recipient phone number in E.164 format (digits only, e.g., 18178419493)
  TEMPLATE_NS   – Template namespace (32-char string from “Namespace” modal)
  TEMPLATE_NM   – Template name (e.g., hourly_trade_alert_us)
  LANG_CODE     – Template language code (e.g., en_US)

Usage:
  python scan_send.py
"""

import os
import sys
import json
import datetime
import requests

def getenv_or_exit(varname):
    val = os.getenv(varname)
    if not val:
        print(f"❌ ERROR: environment variable {varname!r} is not set or empty.", file=sys.stderr)
        sys.exit(1)
    return val

# 1) Load & validate configuration
PHONE_ID      = getenv_or_exit("PHONE_ID")
WABA_TOKEN    = getenv_or_exit("WABA_TOKEN")
USER_NUMBER   = getenv_or_exit("USER_NUMBER")
TEMPLATE_NS   = getenv_or_exit("TEMPLATE_NS")
TEMPLATE_NAME = getenv_or_exit("TEMPLATE_NM")
LANG_CODE     = os.getenv("LANG_CODE", "en_US")

# 2) Build fully-qualified template identifier
template_fqn = f"{TEMPLATE_NS}:{TEMPLATE_NAME}"

# 3) Generate example alert content (replace with real scanner output)
headline = "📰 Market News: Apple beats Q2 earnings"
trade    = "💹 Trade: AAPL – Jul 19 $175/$180 bull-call-spread"
footer   = f"⏰ Note: Risk limited to $95 • {datetime.datetime.utcnow():%H:%M UTC}"

# 4) Construct WhatsApp API request
url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {WABA_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "messaging_product": "whatsapp",
    "to": USER_NUMBER,
    "type": "template",
    "template": {
        "name": template_fqn,
        "language": {"code": LANG_CODE},
        "components": [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": headline},
                {"type": "text", "text": trade},
                {"type": "text", "text": footer}
            ]
        }]
    }
}

# 5) Debug output
print("▶️ URL    :", url)
print("▶️ HEADERS:", json.dumps(headers, indent=2))
print("▶️ PAYLOAD:", json.dumps(payload, indent=2))

# 6) Send the message
response = requests.post(url, headers=headers, json=payload)
print(f"⏱ Status: {response.status_code}")
print(response.text)

# 7) Detailed error feedback
if not response.ok:
    try:
        err = response.json().get("error", {})
        print("❌ API error.message   :", err.get("message"))
        print("❌ API error.code      :", err.get("code"))
        print("❌ API error.error_data:", json.dumps(err.get("error_data", {}), indent=2))
    except Exception as e:
        print("❌ Failed to parse error JSON:", e)
    sys.exit(1)

print("✅ Message sent successfully!")
