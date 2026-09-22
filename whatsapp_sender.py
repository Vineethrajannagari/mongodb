"""
WhatsApp Message Sender - Enhanced version
Sends WhatsApp messages through the official WhatsApp Business Cloud API.

SETUP
  1. pip install fastapi uvicorn requests python-dotenv
     (optional, only for message history: pip install pymongo)
  2. Create a file named .env next to this script:

         WHATSAPP_ACCESS_TOKEN=your_token
         WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
         GRAPH_API_VERSION=v21.0
         MONGODB_URI=            # optional, leave empty to disable

     Get the token and phone number ID from developers.facebook.com ->
     your app -> WhatsApp -> API Setup. Add your friend's number to the
     recipient list there (required in test mode).
     Check Meta's changelog for the current Graph API version.
  3. Run:  python whatsapp_sender.py
     Docs: http://127.0.0.1:8000/docs

TEST
  curl -X POST http://127.0.0.1:8000/send-template \
       -H "Content-Type: application/json" -d '{"phone": "919876543210"}'

  curl -X POST http://127.0.0.1:8000/send-message \
       -H "Content-Type: application/json" \
       -d '{"phone": "919876543210", "message": "Hey bro, how are you?"}'

NOTES
  - Free-form text (/send-message) only works if the recipient messaged your
    number in the last 24 hours. To start a conversation, use /send-template
    (Meta's test number includes a template called "hello_world").
  - "accepted" means WhatsApp queued the message, not that it was delivered.
  - The temporary token from the dashboard expires after about 24 hours.
  - Only message people who agreed to hear from you. Official API only.
"""
import os
import re
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

try:
    from dotenv import load_dotenv

    try:
        load_dotenv()
    except UnicodeDecodeError:
        # Handle cases where .env file has encoding issues
        print("[warn] Could not read .env file due to encoding issues. Using environment variables.")
except ImportError:  # .env support is optional; real environment variables still work
    pass

# ------------------------------------------------------------------ config
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "whatsapp_sender")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))

# ------------------------------------------------- optional MongoDB history
_log = None
if MONGODB_URI:
    try:
        from pymongo import MongoClient

        _log = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)[MONGODB_DB]["messages"]
    except Exception as exc:
        print(f"[warn] could not connect to MongoDB: {exc}")


def log_message(phone: str, text: str, status: str, whatsapp_id: Optional[str] = None, 
                error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Save a send attempt. Does nothing if MongoDB is not configured."""
    if _log is None:
        return
    try:
        doc = {
            "phone": phone,
            "message": text,
            "status": status,
            "whatsapp_message_id": whatsapp_id,
            "error": error,
            "created_at": datetime.now(timezone.utc),
        }
        if metadata:
            doc.update(metadata)
        _log.insert_one(doc)
    except Exception as exc:  # logging must never break sending
        print(f"[warn] could not write message log: {exc}")


# ----------------------------------------------------- WhatsApp API client
class WhatsAppError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def call_whatsapp(payload: dict, retry_count: int = 0) -> dict:
    """Call WhatsApp API with retry logic for transient failures."""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=500,
            detail="Server is missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID.",
        )

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        if retry_count < MAX_RETRIES:
            print(f"[retry] Request failed, attempt {retry_count + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
            return call_whatsapp(payload, retry_count + 1)
        raise WhatsAppError("Could not reach the WhatsApp API", details=str(exc)) from exc

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        error = data.get("error", {})
        # Retry on rate limiting or server errors
        if retry_count < MAX_RETRIES and (response.status_code == 429 or response.status_code >= 500):
            print(f"[retry] API error {response.status_code}, attempt {retry_count + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY * (retry_count + 1))  # Exponential backoff
            return call_whatsapp(payload, retry_count + 1)
        
        raise WhatsAppError(
            error.get("message", "WhatsApp API returned an error"),
            status_code=response.status_code,
            details=error,
        )
    return data


def send_text(to: str, body: str) -> dict:
    return call_whatsapp(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
    )


def send_template(to: str, name: str, language: str, components: Optional[list] = None) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {"name": name, "language": {"code": language}},
    }
    if components:
        payload["template"]["components"] = components
    return call_whatsapp(payload)


def get_message_status(message_id: str) -> dict:
    """Get the status of a previously sent message."""
    if not ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Server is missing WHATSAPP_ACCESS_TOKEN.")
    
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{message_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as exc:
        raise WhatsAppError("Could not reach the WhatsApp API", details=str(exc)) from exc
    
    if not response.ok:
        data = response.json() if response.content else {}
        error = data.get("error", {})
        raise WhatsAppError(
            error.get("message", "WhatsApp API returned an error"),
            status_code=response.status_code,
            details=error,
        )
    
    return response.json()


# ------------------------------------------------------------ request models
class PhoneRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits = re.sub(r"[\s\-()+]", "", value)  # accept "+91 98765-43210"
        if not digits.isdigit() or not 8 <= len(digits) <= 15:
            raise ValueError("phone must include the country code, e.g. 919876543210")
        return digits


class MessageRequest(PhoneRequest):
    message: str = Field(min_length=1, max_length=4096)


class TemplateRequest(PhoneRequest):
    template_name: str = "hello_world"
    language_code: str = "en_US"
    components: Optional[list] = None


class MessageStatusRequest(BaseModel):
    message_id: str = Field(min_length=1)


# ------------------------------------------------------------------ the app
app = FastAPI(
    title="WhatsApp Message Sender",
    version="2.0.0",
    description="Enhanced WhatsApp Business Cloud API integration with retry logic and message tracking"
)


def deliver(phone: str, log_text: str, send_fn, metadata: Optional[Dict[str, Any]] = None) -> dict:
    """Send message with error handling and logging."""
    try:
        result = send_fn()
    except WhatsAppError as exc:
        log_message(phone, log_text, "failed", error=str(exc), metadata=metadata)
        client_error = exc.status_code is not None and 400 <= exc.status_code < 500
        raise HTTPException(
            status_code=400 if client_error else 502,
            detail={
                "error": str(exc),
                "whatsapp_status": exc.status_code,
                "details": exc.details,
            },
        )

    message_id = (result.get("messages") or [{}])[0].get("id")
    log_message(phone, log_text, "accepted", whatsapp_id=message_id, metadata=metadata)
    return {
        "status": "success",
        "message": "WhatsApp message request accepted",
        "whatsapp_message_id": message_id,
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "mongodb_enabled": _log is not None,
        "whatsapp_configured": bool(ACCESS_TOKEN and PHONE_NUMBER_ID),
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY
    }


@app.post("/send-message")
def send_message(data: MessageRequest):
    """Send a free-form text message (requires recipient to have messaged you in last 24h)."""
    return deliver(data.phone, data.message, lambda: send_text(data.phone, data.message))


@app.post("/send-template")
def send_template_endpoint(data: TemplateRequest):
    """Send a template message (can start new conversations)."""
    metadata = {"template_name": data.template_name, "language_code": data.language_code}
    return deliver(
        data.phone,
        f"[template:{data.template_name}]",
        lambda: send_template(data.phone, data.template_name, data.language_code, data.components),
        metadata=metadata
    )


@app.get("/message-status")
def message_status(data: MessageStatusRequest):
    """Get the delivery status of a previously sent message."""
    try:
        result = get_message_status(data.message_id)
        return {
            "status": "success",
            "message_data": result
        }
    except WhatsAppError as exc:
        raise HTTPException(
            status_code=400 if exc.status_code and 400 <= exc.status_code < 500 else 502,
            detail={
                "error": str(exc),
                "whatsapp_status": exc.status_code,
                "details": exc.details,
            },
        )


@app.get("/messages")
def message_history(
    limit: int = Query(50, ge=1, le=200),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get message history from MongoDB (if configured)."""
    if _log is None:
        raise HTTPException(status_code=503, detail="MongoDB is not configured (MONGODB_URI).")
    
    query = {}
    if phone:
        query["phone"] = phone
    if status:
        query["status"] = status
    
    return list(_log.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))


@app.get("/stats")
def message_stats():
    """Get messaging statistics from MongoDB (if configured)."""
    if _log is None:
        raise HTTPException(status_code=503, detail="MongoDB is not configured (MONGODB_URI).")
    
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    stats = list(_log.aggregate(pipeline))
    result = {item["_id"]: item["count"] for item in stats}
    result["total"] = sum(result.values())
    
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
