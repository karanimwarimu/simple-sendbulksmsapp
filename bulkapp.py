from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import uuid

app = FastAPI()

# ---- CONFIG (replace with real values) ----
BULK_SMS_URL = "https://your-provider.com/api/services/sendbulk"
PARTNER_ID = "your_partner_id"
API_KEY = "your_api_key"
SHORTCODE = "your_shortcode"
# -------------------------------------------

class Recipient(BaseModel):
    name: str
    mobile: str

class SMSRequest(BaseModel):
    recipients: List[Recipient]
    message: str


@app.post("/send-bulk")
def send_bulk(request: SMSRequest):
    smslist = []

    for r in request.recipients:
        smslist.append({
            "partnerID": PARTNER_ID,
            "apikey": API_KEY,
            "pass_type": "plain",
            "clientsmsid": str(uuid.uuid4()),  # unique id
            "mobile": r.mobile,
            "message": f"Hi {r.name}, {request.message}",
            "shortcode": SHORTCODE
        })

    payload = {
        "count": len(smslist),
        "smslist": smslist
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(BULK_SMS_URL, json=payload, headers=headers)
        response.raise_for_status()
        return {"success": True, "message": "Messages sent", "provider_response": response.json()}
    except Exception as e:
        return {"success": False, "message": str(e)}
