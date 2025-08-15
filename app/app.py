import os, logging
from datetime import datetime, timedelta, timezone as dtz
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_talisman import Talisman
from itsdangerous import URLSafeSerializer
import requests

from storage import Storage
from ranking import rank_messages
from auth_google import exchange_code_for_id
from gmail_client import fetch_recent_messages, build_gmail_service
from mailer import email_digest

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
Talisman(app, force_https=True, strict_transport_security=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, uid, email, is_admin=False):
        self.id = uid
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    email = session.get("email")
    if not email: return None
    st = Storage()
    is_admin = st.is_admin(email)
    return User(user_id, email, is_admin)

# ---------- Auth ----------
@app.route("/login")
def login():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    redirect_uri = url_for("oauth_callback", _external=True)
    state = URLSafeSerializer(app.secret_key).dumps({"next": request.args.get("next", "/")})
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(f"{k}={requests.utils.quote(v)}" for k,v in params.items())
    return redirect(url)

@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    data = URLSafeSerializer(app.secret_key).loads(state)
    next_url = data.get("next", "/")
    userinfo = exchange_code_for_id(code, url_for("oauth_callback", _external=True))
    email = (userinfo.get("email") or "").lower()
    st = Storage()
    if not st.is_allowed(email):
        # bootstrap: if allowlist empty, add ADMIN_EMAIL and email if matches
        admin = (os.getenv("ADMIN_EMAIL","") or "").lower()
        st.bootstrap_admin(admin)
        if not st.is_allowed(email):
            return "Unauthorized", 403
    user = User(uid=email, email=email, is_admin=st.is_admin(email))
    login_user(user); session["email"] = email
    return redirect(next_url)

@app.route("/logout")
@login_required
def logout():
    logout_user(); session.clear()
    return redirect(url_for("login"))

# ---------- UI shell ----------
@app.route("/")
@login_required
def index():
    return render_template("index.html")
@app.route("/api/preview_email_html")
@login_required
def preview_email_html():
    st = Storage()
    prefs = st.get_prefs(current_user.email)
    gmail = build_gmail_service()
    since = datetime.now(dtz.utc) - timedelta(days=1)
    msgs = fetch_recent_messages(gmail, since)
    ranked = rank_messages(msgs, prefs)
    from mailer import format_html
    theme = prefs.get("email_theme","light"); top_n = int(prefs.get("top_n",20))
    min_score = float(prefs.get("min_score",0.0))
    filtered = [m for m in ranked if m.get("score",0) >= min_score][:top_n]
    
    # breakdown of reasons above threshold
    from collections import Counter
    reason_counts = Counter()
    for m in filtered:
        for r in m.get("reasons", []):
            reason_counts[r] += 1
    threshold_info = "<p style='color:gray;font-size:0.9em'>Importance threshold: %.2f — %d messages shown of %d. Top reasons: %s</p>" % (
        min_score, len(filtered), len(ranked),
        ", ".join(f"{k} ({v})" for k,v in reason_counts.most_common(5))
    )
    html = threshold_info + html
    html = format_html(current_user.email, filtered, theme, top_n)
    return html

@app.route("/settings")
@login_required
def settings_page():
    return render_template("index.html")

@app.route("/admin")
@login_required
def admin_page():
    return render_template("index.html")


# ---------- Admin: manage allowlist ----------
@app.route("/api/admin/users", methods=["GET","POST","DELETE"])
@login_required
def admin_users():
    st = Storage()
    if not st.is_admin(current_user.email): return ("Forbidden", 403)
    if request.method == "GET":
        return jsonify(st.get_allowlist())
    if request.method == "POST":
        data = request.get_json(force=True)
        st.add_allowed(data.get("email","").lower())
        return jsonify({"ok": True})
    # DELETE
    data = request.get_json(force=True)
    st.remove_allowed(data.get("email","").lower())
    return jsonify({"ok": True})

# ---------- Preferences ----------
@app.route("/api/prefs", methods=["GET", "POST"])
@login_required
def prefs():
    st = Storage()
    if request.method == "GET":
        return jsonify(st.get_prefs(current_user.email))
    data = request.get_json(force=True)
    st.save_prefs(current_user.email, data)
    return jsonify({"ok": True})

# ---------- Digest ----------
@app.route("/api/digest")
@login_required
def api_digest():
    days = int(request.args.get("days", 1))
    since = datetime.now(dtz.utc) - timedelta(days=days)
    gmail = build_gmail_service()
    msgs = fetch_recent_messages(gmail, since)
    st = Storage()
    prefs = st.get_prefs(current_user.email)
    ranked = rank_messages(msgs, prefs)
    min_score = float(prefs.get('min_score', 0.0))
    ranked_filt = [m for m in ranked if (m.get('score',0) >= min_score)]
    st.save_digest(current_user.email, ranked)
    return jsonify({"messages": ranked_filt, "total": len(ranked), "shown": len(ranked_filt)})

@app.route("/api/run_digest", methods=["POST"])
def run_digest_webhook():
    api_key = request.headers.get("X-API-Key", "")
    if api_key != os.getenv("X_API_KEY", ""):
        return "Forbidden", 403
    gmail = build_gmail_service()
    since = datetime.now(dtz.utc) - timedelta(days=1)
    msgs = fetch_recent_messages(gmail, since)
    st = Storage()
    # run for all allowed users
    recipients = st.get_allowlist()
    sent = 0
    for email in recipients:
        prefs = st.get_prefs(email)
        ranked = rank_messages(msgs, prefs)
        st.save_digest(email, ranked)
        # email out
        try:
            email_digest(email, ranked, prefs)
            sent += 1
        except Exception as e:
            logger.exception("SendGrid failed for %s: %s", email, e)
    # retention cleanup
    st.cleanup_retention(days=180)
    return jsonify({"ok": True, "recipients": len(recipients), "emailed": sent})

@app.route("/static/dist/<path:path>")
def serve_dist(path):
    return send_from_directory(os.path.join(app.static_folder, "dist"), path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","5000")), debug=True)

@app.route("/api/preview_digest")
@login_required
def preview_digest():
    gmail = build_gmail_service()
    since = datetime.now(dtz.utc) - timedelta(days=1)
    msgs = fetch_recent_messages(gmail, since)
    st = Storage()
    prefs = st.get_prefs(current_user.email)
    ranked = rank_messages(msgs, prefs)
    from mailer import format_html
    theme = prefs.get('email_theme','light')
    top_n = int(prefs.get('top_n',20))
    html = format_html(current_user.email, ranked, theme, top_n)
    return html

@app.route("/api/admin/analytics")
@login_required
def admin_analytics():
    if current_user.email.lower() != os.getenv("ADMIN_EMAIL", "").lower():
        return "Forbidden", 403
    st = Storage()
    all_users = st.get_all_users()
    stats = {}
    for u in all_users:
        digests = st.get_digests(u)
        stats[u] = {
            "digests": len(digests),
            "messages_total": sum(len(d.get('messages',[])) for d in digests),
        }
    return jsonify(stats)
