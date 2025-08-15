import os, requests
import azure.functions as func

app = func.FunctionApp()

# PT timezone via Function App setting TZ=America/Los_Angeles
@app.schedule(schedule="0 0 5,12,16 * * *", arg_name="timer")
def run_digest(timer: func.TimerRequest) -> None:
    base = os.environ.get("BACKEND_BASE_URL")
    api_key = os.environ.get("X_API_KEY")
    if not base or not api_key:
        print("Missing BACKEND_BASE_URL or X_API_KEY"); return
    try:
        r = requests.post(f"{base}/api/run_digest", headers={"X-API-Key": api_key}, timeout=30)
        print("Digest trigger status:", r.status_code, r.text[:200])
    except Exception as e:
        print("Error calling backend:", e)
