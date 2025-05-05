# scan_send.py  – first‑run demo
import os, requests, json, datetime

PHONE_ID = os.environ["PHONE_ID"]
TOKEN    = os.environ["WABA_TOKEN"]
TO       = os.environ["USER_NUMBER"]

headline = "🛢️ OPEC+ speeds output – Bearish"
trade    = "XLE · Sell 95C / Buy 100C Jul‑18 · Credit 0.53 · POP 78 % · Risk $47"
footer   = "Test alert " + datetime.datetime.utcnow().strftime("%H:%M UTC")

body = {
  "messaging_product": "whatsapp",
  "to": TO,
  "type": "template",
  "template": {
    "name": "hourly_trade_alert",
    "language": { "code": "en_US" },
    "components": [{
      "type": "body",
      "parameters": [
        { "type": "text", "text": headline },
        { "type": "text", "text": trade },
        { "type": "text", "text": footer }
      ]
    }]
  }
}

url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
r = requests.post(url,
                  headers={"Authorization": f"Bearer {TOKEN}",
                           "Content-Type": "application/json"},
                  data=json.dumps(body))
print("Status:", r.status_code, r.text)
