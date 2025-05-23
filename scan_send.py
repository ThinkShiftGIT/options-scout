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
        print(f"❌ ERROR: environment variable {varname!r} is not set or empty. This is required for script operation. Please ensure it is set in your environment or as a GitHub secret.", file=sys.stderr)
        sys.exit(1)
    return val

# 1) Load & validate configuration
PHONE_ID      = getenv_or_exit("PHONE_ID")
WABA_TOKEN    = getenv_or_exit("WABA_TOKEN")
USER_NUMBER   = getenv_or_exit("USER_NUMBER")
LANG_CODE     = os.getenv("LANG_CODE", "en_US") # Default to en_US if not set

# Handle TEMPLATE_NS and TEMPLATE_NM with warnings and placeholders
TEMPLATE_NS = os.getenv("TEMPLATE_NS")
if not TEMPLATE_NS:
    TEMPLATE_NS = "your_template_namespace_here"
    print(f"⚠️ WARNING: Environment variable 'TEMPLATE_NS' is not set. Using placeholder value '{TEMPLATE_NS}'. The script will likely fail to send a message unless these are correctly configured.", file=sys.stderr)

TEMPLATE_NAME = os.getenv("TEMPLATE_NM")
if not TEMPLATE_NAME:
    TEMPLATE_NAME = "your_template_name_here"
    print(f"⚠️ WARNING: Environment variable 'TEMPLATE_NM' is not set. Using placeholder value '{TEMPLATE_NAME}'. The script will likely fail to send a message unless these are correctly configured.", file=sys.stderr)


# 2) Build fully-qualified template identifier
# This combines the template namespace and name, required by the API.
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
# Construct the message payload
# See: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages#message-templates
payload = {
    "messaging_product": "whatsapp",  # Identifies the WhatsApp product
    "to": USER_NUMBER,                # Recipient's phone number
    "type": "template",               # Message type is a template
    "template": {
        "name": template_fqn,         # Fully-qualified template name
        "language": {"code": LANG_CODE}, # Language code for the template
        "components": [{              # Components allow for dynamic content in templates
            "type": "body",           # This component is for the body of the message
            "parameters": [           # Parameters to fill in template placeholders
                {"type": "text", "text": headline}, # First body parameter
                {"type": "text", "text": trade},    # Second body parameter
                {"type": "text", "text": footer}    # Third body parameter
            ]
        }]
    }
}

# 5) Debug output
print("▶️ URL    :", url)
print("▶️ HEADERS:", json.dumps(headers, indent=2))
print("▶️ PAYLOAD:", json.dumps(payload, indent=2))

# 6) Send the message
# This is where the script makes the actual HTTP POST request to the WhatsApp API.
try:
    response = requests.post(url, headers=headers, json=payload, timeout=10) # Added timeout
    print(f"⏱ Status: {response.status_code}")
    print(response.text) # Print raw response text

    # 7) Detailed error feedback
    if not response.ok:
        try:
            err_json = response.json() # Attempt to parse JSON first
            error_details = err_json.get("error", {})
            print("❌ API error.message   :", error_details.get("message"))
            print("❌ API error.code      :", error_details.get("code"))
            print("❌ API error.type      :", error_details.get("type"))
            print("❌ API error.fbtrace_id:", error_details.get("fbtrace_id"))
            print("❌ API error.error_data:", json.dumps(error_details.get("error_data", {}), indent=2))
        except json.JSONDecodeError: # If response is not JSON
            print("❌ Failed to parse error response as JSON. Raw response above.")
        except Exception as e: # Catch other potential errors during error parsing
            print(f"❌ An unexpected error occurred while parsing the error response: {e}")
        sys.exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"❌ ERROR: Connection error. Could not connect to {url}. Details: {e}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.Timeout as e:
    print(f"❌ ERROR: Request timed out while trying to reach {url}. Details: {e}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as e: # Catch other request-related errors
    print(f"❌ ERROR: An error occurred during the API request to {url}. Details: {e}", file=sys.stderr)
    sys.exit(1)


    print("✅ Message sent successfully!")

if __name__ == "__main__":
    # This datetime object is created here to allow for easier mocking in tests.
    # If it were created directly inside main(), it would be harder to patch.
    # By passing it as an argument, we can control its value during testing.
    main(current_time_utc=datetime.datetime.utcnow())
