from typing import List, Dict
from datetime import datetime
from email.utils import parsedate_to_datetime

DEFAULT_WEIGHTS = {
    "vip": 5.0,
    "blocked": -10.0,
    "always_kw": 3.0,
    "mute_kw": -4.0,
    "urgent_kw": 3.0,
    "money_kw": 2.5,
    "mention_kw": 2.0,
    "recency_decay_per_hour": -0.05,
}

URGENT_TERMS = ["urgent", "asap", "immediately", "deadline", "due", "action required"]
MONEY_TERMS = ["invoice", "payment", "paid", "unpaid", "bill", "receipt", "quote", "estimate"]

def _score(msg: Dict, prefs: Dict, weights: Dict) -> (float, List[str]):
    score = 0.0; reasons = []
    sender = (msg.get("from") or "").lower()
    subj = (msg.get("subject") or "").lower()
    snip = (msg.get("snippet") or "").lower()
    text = f"{subj} {snip}"

    vip = [s.lower() for s in prefs.get("vip_senders", [])]
    blocked = [s.lower() for s in prefs.get("blocked_senders", [])]
    always = [k.lower() for k in prefs.get("always_keywords", [])]
    mute = [k.lower() for k in prefs.get("mute_keywords", [])]

    if any(v in sender for v in vip):
        score += weights["vip"]; reasons.append("VIP")
    if any(b in sender for b in blocked):
        score += weights["blocked"]; reasons.append("Blocked sender")
    if any(k in text for k in always):
        score += weights["always_kw"]; reasons.append("Always-show keyword")
    if any(k in text for k in mute):
        score += weights["mute_kw"]; reasons.append("Muted keyword")
    if any(k in text for k in URGENT_TERMS):
        score += weights["urgent_kw"]; reasons.append("Deadline/Urgent")
    if any(k in text for k in MONEY_TERMS):
        score += weights["money_kw"]; reasons.append("Billing/Invoice")

    try:
        dt = parsedate_to_datetime(msg.get("date")) or datetime.utcnow()
        hours = max(0.0, (datetime.utcnow() - dt.replace(tzinfo=None)).total_seconds()/3600.0)
        score += hours * weights["recency_decay_per_hour"]
    except Exception:
        pass

    urgency_bias = float(prefs.get("urgency_bias", 0.5))
    score += urgency_bias * 0.5
    return score, reasons

def rank_messages(messages: List[Dict], prefs: Dict) -> List[Dict]:
    weights = DEFAULT_WEIGHTS.copy()
    weights.update(prefs.get("weights", {}))
    ranked = []
    for m in messages:
        s, reasons = _score(m, prefs, weights)
        ranked.append({**m, "score": round(s, 3), "reasons": reasons})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
