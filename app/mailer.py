import os
from typing import List, Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def format_html(email: str, messages: List[Dict], theme: str = 'light', top_n: int = 20) -> str:
    rows = []
    for m in messages[:top_n]:
        reasons = " • ".join(m.get("reasons", []))
        rows.append(f"<tr><td style='padding:8px;border-bottom:1px solid #eee'>{m.get('from','')}</td>"
                    f"<td style='padding:8px;border-bottom:1px solid #eee'><b>{m.get('subject','(no subject)')}</b><br>"
                    f"<div style='color:#555'>{m.get('snippet','')}</div>"
                    f"<div style='font-size:12px;color:#777;margin-top:4px'>{reasons}</div></td></tr>")
    table = "<table width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse'>" + "".join(rows) + "</table>"
    return f"<div style='font-family:system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif'><h2>Your Gmail Digest</h2>{table}<p style='color:#888'>{min(top_n,len(messages))} shown.</p></div>"

def email_digest(recipient: str, messages: List[Dict], prefs: Dict):
    threshold = float((prefs or {}).get('importance_threshold', 0.0))
    if threshold:
        messages = [m for m in messages if m.get('score', 1.0) >= threshold]
    if not SENDGRID_API_KEY: return
    theme = (prefs or {}).get('email_theme','light')
    top_n = int((prefs or {}).get('top_n', 20))
    min_score = float((prefs or {}).get('min_score', 0.0))
    filtered = [m for m in messages if (m.get('score', 0) >= min_score)]
    html = format_html(recipient, filtered, theme, top_n)
    message = Mail(
        from_email=("no-reply@gmail-digest", "Gmail Digest Bot"),
        to_emails=recipient,
        subject="Your Gmail Digest",
        html_content=html
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)
