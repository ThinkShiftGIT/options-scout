#!/usr/bin/env python3
"""
scan_send.py  ▸  minimal WhatsApp‑Cloud‑API sender
──────────────────────────────────────────────────
▪ Reads your secrets from environment variables
▪ Assembles one templated alert
▪ POSTs it to the WhatsApp Business Cloud API

REQUIRED SECRETS  (add in GitHub → Settings → Secrets & variables → Actions)

  PHONE_ID      – numeric phone‑ID that owns the template
  WABA_TOKEN    – permanent system‑user token (Bearer)
  USER_NUMBER   – customer number with country code (18175551234)
  TEMPLATE_NAME – e.g. hourly_trade_alert_us
  LANG_CODE     – e.g. en_US
  NAMESPACE     – 32‑char namespace shown in *Namespace* modal

Usage:   python scan_send.py
"""

import os, json, datetime, textwrap, requests, sys

# ╭──────────────────────────────────────────────╮
# │ 1.  pull the secrets                         │
# ╰──────────────────────────────────────────────╯
PHONE_ID      = os.getenv("PHONE_ID")
TOKEN         = os.getenv("WABA_TOKEN")
TO            = os.getenv("USER_NUMBER")
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME")
LANG_CODE     = os.getenv("LANG_CODE", "en_US")
NAMESPACE     = os.getenv("NAMESPACE")           # optional but recommended

# rudimentary guard‑rails
for var, val in [("PHONE_ID",PHONE_ID),("TOKEN",TOKEN),
                 ("TO",TO),("TEMPLATE_NAME",TEMPLATE_NAME)]:
    if not val:
        sys.exit(f"❌  env var {var} missing")

# ╭──────────────────────────────────────────────╮
# │ 2.  craft example alert content              │
# ╰──────────────────────────────────────────────╯
headline = "📊 Market News: Jobs report beats estimates"
trade    = "🟢 Trade: SPY Jun 28 525/530 bull‑call‑spread"
footer   = f"⏱ Note: Risk limited to $200 • {datetime.datetime.utcnow():%H:%M} UTC"

# ╭──────────────────────────────────────────────╮
# │ 3.  build WhatsApp Cloud API payload         │
# ╰──────────────────────────────────────────────╯
template_fqn = f"{NAMESPACE}:{TEMPLATE_NAME}" if NAMESPACE else TEMPLATE_NAME

body = {
    "messaging_product": "whatsapp",
    "to": TO,
    "type": "template",
    "template": {
        "name": template_fqn,
        "language": { "code": LANG_CODE },
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

# ╭──────────────────────────────────────────────╮
# │ 4.  POST                                     │
# ╰──────────────────────────────────────────────╯
url     = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
headers = { "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json" }

resp = requests.post(url, headers=headers, data=json.dumps(body))
print("Status:", resp.status_code, resp.text)
resp.raise_for_status()     # will error‑out the GitHub Action if not 2xx
