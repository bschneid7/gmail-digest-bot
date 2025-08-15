import os
from datetime import datetime, timezone as dtz
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def build_gmail_service():
    creds = Credentials(
        None,
        refresh_token=os.environ.get("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def fetch_recent_messages(service, since: datetime) -> List[Dict]:
    now = datetime.now(dtz.utc)
    delta_days = max(1, int((now - since).total_seconds() // 86400))
    q = f"newer_than:{delta_days}d"
    results = service.users().messages().list(userId="me", q=q, maxResults=100).execute()
    msgs = []
    for item in results.get("messages", []):
        msg = service.users().messages().get(userId="me", id=item["id"], format="metadata", metadataHeaders=["Subject","From","To","Date"]).execute()
        payload = msg.get("payload", {})
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        subject = headers.get("subject",""); from_ = headers.get("from",""); to = headers.get("to",""); date = headers.get("date","")
        snippet = msg.get("snippet",""); labels = msg.get("labelIds", [])
        msgs.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "subject": subject,
            "from": from_,
            "to": to,
            "date": date,
            "snippet": snippet,
            "labels": labels,
            "historyId": msg.get("historyId"),
            "internalDate": msg.get("internalDate"),
        })
    return msgs
