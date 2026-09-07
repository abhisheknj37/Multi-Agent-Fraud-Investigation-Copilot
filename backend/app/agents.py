import sqlite3, json, datetime, math
from .db import get_db

WEIGHTS = {
    "amount": 0.22, "geography": 0.18, "merchant": 0.14, "time": 0.12,
    "velocity": 0.14, "device": 0.08, "ip": 0.06, "duplicate": 0.06,
}


def _signals(db, t):
    customer_id = t["customer_id"]
    locations = [x.strip() for x in (t["normal_locations"] or "").split(",") if x.strip()]
    merchants = [x.strip() for x in (t["normal_merchants"] or "").split(",") if x.strip()]
    amount = 1 if t["amount"] > max(t["avg_amount"] * 5, t["max_amount"] * 1.5) else (0.6 if t["amount"] > t["avg_amount"] * 3 else 0)
    geography = 1 if t["location"] not in locations else 0
    merchant = 0.8 if t["merchant_category"] not in merchants else 0
    dt = datetime.datetime.fromisoformat(t["timestamp"])
    time_signal = 1 if dt.hour < 6 or dt.hour >= 23 else 0
    cutoff=(datetime.datetime.fromisoformat(t["timestamp"])-datetime.timedelta(minutes=10)).isoformat(); recent=db.execute("SELECT COUNT(*) c FROM transactions WHERE customer_id=? AND timestamp>=?", (customer_id, cutoff)).fetchone()["c"]
    velocity = 1 if recent >= 3 else (0.5 if recent == 2 else 0)
    device = 0.8 if t["device_id"] != "DEV-A" else 0
    ip = 0.6 if not t["ip_address"].startswith("10.") else 0
    ts=datetime.datetime.fromisoformat(t["timestamp"]); lo=(ts-datetime.timedelta(minutes=2)).isoformat(); hi=(ts+datetime.timedelta(minutes=2)).isoformat(); duplicate=db.execute("SELECT COUNT(*) c FROM transactions WHERE customer_id=? AND amount=? AND merchant_category=? AND timestamp BETWEEN ? AND ?", (customer_id,t["amount"],t["merchant_category"],lo,hi)).fetchone()["c"] > 1
    return {"amount": amount, "geography": geography, "merchant": merchant, "time": time_signal, "velocity": velocity, "device": device, "ip": ip, "duplicate": 0.7 if duplicate else 0}


def compute_score_only(transaction_id):
    db = get_db()
    t = db.execute("""SELECT t.*, c.avg_amount, c.max_amount, c.normal_locations, c.normal_merchants
                     FROM transactions t JOIN customers c ON c.id=t.customer_id WHERE t.id=?""", (transaction_id,)).fetchone()
    if not t:
        return 0
    s = _signals(db, t)
    return round(min(100, 100 * sum(WEIGHTS[k] * s[k] for k in WEIGHTS)), 1)


def investigate_transaction(transaction_id):
    db = get_db()
    t = db.execute("""SELECT t.*, c.name customer_name, c.avg_amount, c.max_amount,
                    c.normal_locations, c.normal_merchants, c.disputes, c.prior_flags,
                    c.account_age_days
                    FROM transactions t JOIN customers c ON c.id=t.customer_id WHERE t.id=?""", (transaction_id,)).fetchone()
    if not t:
        return None
    signals = _signals(db, t)
    score = round(min(100, 100 * sum(WEIGHTS[k] * signals[k] for k in WEIGHTS)), 1)
    evidence = []

    def add(category, severity, explanation, metric):
        evidence.append({"category": category, "severity": severity, "explanation": explanation, "metric": metric})

    if signals["amount"]:
        add("Amount anomaly", "HIGH", f"Current amount ₹{t['amount']:,.0f} is far above the customer's average ₹{t['avg_amount']:,.0f} and historical maximum ₹{t['max_amount']:,.0f}.", "amount")
    if signals["geography"]:
        add("Geographic anomaly", "HIGH", f"Transaction location {t['location']} is outside normal locations: {t['normal_locations']}.", "location")
    if signals["merchant"]:
        add("Merchant anomaly", "MEDIUM", f"Merchant category {t['merchant_category']} differs from normal categories: {t['normal_merchants']}.", "merchant")
    dt = datetime.datetime.fromisoformat(t["timestamp"])
    if signals["time"]:
        add("Time anomaly", "HIGH", f"Transaction occurred at {dt:%H:%M}, outside typical daytime activity.", "time")
    cutoff=(datetime.datetime.fromisoformat(t["timestamp"])-datetime.timedelta(minutes=10)).isoformat(); recent=db.execute("SELECT COUNT(*) c FROM transactions WHERE customer_id=? AND timestamp>=?", (t["customer_id"], cutoff)).fetchone()["c"]
    if signals["velocity"]:
        add("Velocity anomaly", "HIGH", f"{recent} transactions occurred within a 10-minute window.", "velocity")
    if signals["device"]:
        add("Device anomaly", "MEDIUM", f"Device {t['device_id']} differs from the demo customer's usual device profile.", "device")
    if signals["ip"]:
        add("IP anomaly", "MEDIUM", f"IP address {t['ip_address']} is outside the trusted demo network range.", "ip")
    if signals["duplicate"]:
        add("Duplicate transaction", "HIGH", "A matching customer, amount and merchant transaction exists within ±2 minutes.", "duplicate")

    # Network Intelligence Agent: derive connected entities and simple concentration risk.
    related = db.execute("""SELECT COUNT(*) c FROM transactions WHERE (device_id=? OR ip_address=?) AND customer_id<>?""", (t["device_id"], t["ip_address"], t["customer_id"])).fetchone()["c"]
    network_risk = min(1.0, related / 3) if related else 0
    if related:
        add("Network link", "HIGH" if related >= 3 else "MEDIUM", f"The device/IP fingerprint is connected to {related} transaction(s) from other customers.", "network")

    breakdown = [{"factor": k, "weight": round(WEIGHTS[k] * 100), "signal": signals[k], "contribution": round(WEIGHTS[k] * signals[k] * 100, 1)} for k in WEIGHTS]
    risk = "HIGH" if score >= 75 else ("MEDIUM" if score >= 50 else "LOW")
    recommendation = "Manual review / escalate" if risk == "HIGH" else ("Review supporting evidence" if risk == "MEDIUM" else "Likely normal; clear if no other concerns")
    case_id = "CASE-" + transaction_id[4:]
    now = datetime.datetime.now().isoformat(timespec="seconds")
    db.execute("INSERT INTO cases(id,transaction_id,status,assigned_analyst,analyst_note,created_at,updated_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING", (case_id, transaction_id, "New", "analyst", "", now, now))
    for item in evidence:
        exists = db.execute("SELECT 1 FROM evidence_vault WHERE transaction_id=? AND category=? AND explanation=?", (transaction_id, item["category"], item["explanation"])).fetchone()
        if not exists:
            db.execute("INSERT INTO evidence_vault(transaction_id,category,severity,explanation,source) VALUES(?,?,?,?,?)", (transaction_id, item["category"], item["severity"], item["explanation"], "fraud_ai_engine"))
    db.execute("INSERT INTO audit_log(action,entity_id,details) VALUES(?,?,?)", ("MULTI_AGENT_INVESTIGATION", transaction_id, json.dumps({"score": score, "agents": ["Transaction Pattern Agent", "Customer History Agent", "Risk Scoring Agent", "Network Intelligence Agent"], "evidence_count": len(evidence)})))
    db.commit()
    return {
        "transaction": dict(t), "risk_score": score, "risk_level": risk,
        "confidence": round(min(98, max(55, score + 7)), 1), "recommendation": recommendation, "case_id": case_id,
        "agents": {
            "transaction_pattern": {"status": "completed", "findings": [e for e in evidence if e["metric"] in ["amount", "location", "merchant", "time", "velocity"]]},
            "customer_history": {"status": "completed", "findings": [{"category": "Spending baseline", "detail": f"Average ₹{t['avg_amount']:,.0f}; maximum ₹{t['max_amount']:,.0f}"}, {"category": "Prior disputes", "detail": str(t["disputes"])}, {"category": "Prior flags", "detail": str(t["prior_flags"])}, {"category": "Account age", "detail": f"{t['account_age_days']} days"}]},
            "risk_scoring": {"status": "completed", "method": "Weighted evidence aggregation", "score": score, "breakdown": breakdown},
            "network_intelligence": {"status": "completed", "related_transactions": related, "network_risk": round(network_risk, 2)},
        },
        "evidence": evidence,
        "anomaly_detection": {
            "detected": bool(evidence),
            "count": len(evidence),
            "signals": [item["metric"] for item in evidence],
        },
        "typologies": [
            typology for typology, condition in [
                ("Account takeover", signals["device"] and signals["ip"]),
                ("Geographic anomaly", signals["geography"] and signals["ip"]),
                ("Transaction laundering / mule activity", signals["velocity"] and signals["amount"]),
                ("Card-not-present risk", signals["device"] and t["payment_method"] == "Card"),
            ] if condition
        ],
        "audit": {"generated_at": now, "trace": ["Transaction Pattern Agent", "Customer History Agent", "Risk Scoring Agent", "Network Intelligence Agent", "Evidence Trail", "Human Analyst"]},
    }
