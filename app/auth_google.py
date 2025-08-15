import os, requests

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

def exchange_code_for_id(code: str, redirect_uri: str) -> dict:
    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).json()
    id_token = token_resp.get("id_token")
    if not id_token: raise RuntimeError("Failed to exchange code for token")
    userinfo = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}).json()
    return {"email": userinfo.get("email"), "name": userinfo.get("name")}
