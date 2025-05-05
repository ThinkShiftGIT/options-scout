# scan_send.py  – WhatsApp Cloud API “hourly_trade_alert” demo
# -----------------------------------------------------------
# Requires three GitHub‑Actions secrets:
#   PHONE_ID    – WhatsApp test phone‑number ID (looks like 123456789012345)
#   WABA_TOKEN  – System‑user access token (Never‑expire)
#   USER_NUMBER – Recipient number in E.164 format, e.g. 18178419493
#
# Run locally:  export PHONE_ID=… WABA_TOKEN=… USER_NUMBER=… && python scan_send.py

import os, requests, json, datetime
from textwrap import dedent

PHONE_ID = os.environ["PHONE_ID"]
TOKEN     = os.environ["WABA_TOKEN"]
TO        = os.environ["USER_NUMBER"]

# ── ► example content you would generate with your scanner ◄ ──
headline = "📈 Market News: Apple beats Q2 earnings"
trade    = "📊 Trade: AAPL – Jun 21 $175/$180 bull‑call‑spread"
footer   = f"⏰ Note: Risk limited to $95, 72 % POP – {datetime.datetime.utcnow():%H:%M UTC}"

body = {
    "messaging_product": "whatsapp",
    "to": TO,
    "type": "template",
    "template": {
        "name": "hourly_trade_alert",          # ⭆ EXACT name from Manager
        "language": { "code": "en" },          # use 2‑letter code
        "components": [{
            "type": "body",
            "parameters": [
                { "type": "text", "text": headline },  # {{1}}
                { "type": "text", "text": trade },     # {{2}}
                { "type": "text", "text": footer }     # {{3}}
            ]
        }]
    }
}

url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type":  "application/json"
}

print("Sending to WhatsApp…")
resp = requests.post(url, headers=headers, data=json.dumps(body))

print("HTTP status:", resp.status_code)
print(resp.text if resp.text.strip() else "<empty response>")

if resp.ok:
    print("✅  Message accepted by API.")
else:
    print("❌  Error – review status code & message above.")
