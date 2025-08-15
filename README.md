# Gmail Digest Bot — Azure, Google Login, Cosmos DB, SendGrid

Matches your selections:
- **Google OIDC** login
- **Multi-user allowlist** (stored in Cosmos DB; initial admin set via env `ADMIN_EMAIL`)
- **Cosmos DB serverless (Core/SQL API)** for prefs/history/allowlist
- **SendGrid** outbound digests at 5:00 / 12:00 / 16:00 PT
- **6‑month retention** cleanup on each run
- **React + Tailwind** UI with Settings (VIPs, deadlines, billing terms)

## Environment (App Service)
- `FLASK_SECRET_KEY`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `ADMIN_EMAIL` (bootstrap admin who can add allowed emails)
- `X_API_KEY` (Functions -> backend)
- `COSMOS_URL`, `COSMOS_KEY`, `COSMOS_DB=GmailDigest`, `COSMOS_CONTAINER=Data`
- `SENDGRID_API_KEY`
- `TZ=America/Los_Angeles`

## Functions App
- `BACKEND_BASE_URL=https://<app>.azurewebsites.net`
- `X_API_KEY` (same as app)
- `TZ=America/Los_Angeles`

## Local Dev (summary)
```
cd web && npm install && npm run build
cd ../app && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python app.py
```
