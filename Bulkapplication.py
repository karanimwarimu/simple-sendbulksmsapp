from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import requests
import uuid
import os
import uvicorn
import logging 
import sys 
from datetime import datetime , timezone
# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bulk_sms.txt"),  # persistent log file
        logging.StreamHandler(sys.stdout)  # console / Render logs
    ]
)


app = FastAPI()

# ---- REAL CONFIG ----
BULK_SMS_URL = "https://quicksms.advantasms.com/api/services/sendbulk/"
PARTNER_ID = "11945"
API_KEY = "e00720e5316dafe1ed04c3fc2fe6cf4e"
SHORTCODE = "AdvantaSM"
# ----------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "static", "bulkweb.html")

# ---------- MODELS ----------
class Recipient(BaseModel):
    name: str
    mobile: str

class SMSRequest(BaseModel):
    recipients: List[Recipient]
    message: str


# ---------- ROUTES ----------
@app.get("/")
async def root():
    """Serve the HTML page (frontend)."""
    return FileResponse(HTML_FILE)

    """ test receiving texts
@app.post("/send-bulk")
def send_bulk(sms_request: SMSRequest, req: Request):
    client_host = req.client.host

    # Log incoming request
    logging.info(f"Received bulk SMS request from IP: {client_host}")
    logging.info(f"Recipients: {[r.dict() for r in sms_request.recipients]}")
    logging.info(f"Message: {sms_request.message}")
    return {"success" : True}
"""

@app.post("/send-bulk")
def send_bulk(sms_request: SMSRequest, req: Request):
    client_host = req.client.host
    time_received = datetime.now(timezone.utc)
    # Log incoming request
    logging.info(f"Received bulk SMS request from IP: {client_host} at time : {time_received}")
    logging.info(f"Recipients: {[r.dict() for r in sms_request.recipients]}")
    logging.info(f"Message: {sms_request.message}")

    smslist = []
    for r in sms_request.recipients:
        smslist.append({
            "partnerID": PARTNER_ID,
            "apikey": API_KEY,
            "pass_type": "plain",
            "clientsmsid": str(uuid.uuid4()),  # unique per message
            "mobile": r.mobile,
            "message": f"Hi {r.name}, {sms_request.message}",
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
        logging.info(f"Sent {len(smslist)} messages successfully. Provider response: {response.json()}")
        return {
            "success": True,
            "message": f"Messages sent to {len(smslist)} recipients",
            "provider_response": response.json()
        }
    except Exception as e:
        logging.error(f"Failed to send messages: {e}")
        return {"success": False, "message": str(e)}

    # ---------- DEV SERVER ----------
