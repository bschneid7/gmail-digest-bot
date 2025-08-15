import os, webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import http.server, socketserver
import requests

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or input("Enter GOOGLE_CLIENT_ID: ").strip()
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or input("Enter GOOGLE_CLIENT_SECRET: ").strip()
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "https://www.googleapis.com/auth/gmail.readonly openid email profile"

auth_params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPE,
    "access_type": "offline",
    "prompt": "consent",
}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/callback"):
            qs = parse_qs(urlparse(self.path).query)
            code = qs.get("code", [""])[0]
            token_resp = requests.post("https://oauth2.googleapis.com/token", data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            }).json()
            refresh = token_resp.get("refresh_token")
            self.send_response(200); self.end_headers()
            self.wfile.write(f"Refresh token:<br><pre>{refresh}</pre>".encode())
            print("\nGMAIL_REFRESH_TOKEN =", refresh)
        else:
            self.send_response(200); self.end_headers()
            self.wfile.write(b"OK")

if __name__ == "__main__":
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(auth_params)
    print("Opening:", url)
    webbrowser.open(url)
    with socketserver.TCPServer(("localhost", 8080), Handler) as httpd:
        print("Listening on http://localhost:8080 ...")
        httpd.handle_request()
