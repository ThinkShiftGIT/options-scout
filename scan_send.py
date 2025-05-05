#!/usr/bin/env python3
"""
scan_send.py – WhatsApp Cloud API Alert Sender

This script reads configuration from environment variables and sends
a templated WhatsApp message via the WhatsApp Business Cloud API.

Required environment variables (set as GitHub Actions secrets or local env):
  PHONE_ID      – WhatsApp phone-number ID (from API Setup)
  WABA_TOKEN    – Permanent system-user access token (Never expires)
  USER_NUMBER   – Recipient phone number in E.164 format (digits only, e.g., 18178419493)
  TEMPLATE_NS   – Template namespace (32-char string from "Namespace" modal)
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

# 1. Load configuration
PHONE_ID    = os.getenv("PHONE_ID")
TOKEN       = os.getenv("WABA_TOKEN")
TO_NUMBER   = os.getenv("USER_NUMBER")
NAMESPACE   = os.getenv("TEMPLATE_NS")
TEMPLATE    = os.getenv("TEMPLATE_NM")
LANG_CODE   = os.getenv("LANG_CODE", "en_US")

# 2. Validate required vars
missing = [name for name,val in {
    "PHONE_ID": PHONE_ID,
    "WABA_TOKEN": TOKEN,
    "USER_NUMBER": TO_NUMBER,
    "TEMPLATE_NS": NAMESPACE,
    "TEMPLATE_NM": TEMPLATE
}.items() if not val]
if missing:
    sys.exit(f"❌ Missing environment variable(s): {', '.join(missing)}")

# 3. Build fully-qualified template identifier
template_fqn = f"{NAMESPACE}:{TEMPLATE}"

# 4. Example alert data (replace with real scanner output)
headline = "📰 Market News: Apple beats Q2 earnings"
trade    = "💹 Trade: AAPL Jul 19 $175/$180 bull-call-spread"
footer   = f"⏰ Note: Risk limited to $95 • {datetime.datetime.utcnow():%H:%M UTC}"

# 5. Construct WhatsApp Cloud API payload
payload = {
    "messaging_product": "whatsapp",
    "to": TO_NUMBER,
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

url     = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 6. Send the message
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(f"Status: {response.status_code}")
print(response.text)

if response.ok:
    print("✅ Message sent successfully.")
else:
    print("❌ Failed to send message.")
    sys.exit(1)
