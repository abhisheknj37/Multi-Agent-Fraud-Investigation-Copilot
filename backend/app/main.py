from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import json
import csv
import io
import datetime

from .db import init_db, get_db
from .agents import investigate_transaction
from .reports import make_report


# ============================================================
# PATHS
# ============================================================

# Project root:
# D:\newproj
BASE = Path(__file__).resolve().parents[2]

# React production build:
# D:\newproj\frontend-react\dist
FRONTEND = BASE / "frontend-react" / "dist"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Financial Crime Sentinel",
    version="2.0.0"
)


# ============================================================
# SERVE REACT FRONTEND
# ============================================================

# React/Vite puts JavaScript, CSS and other static files
# inside dist/assets.
if FRONTEND.exists():
    assets_dir = FRONTEND / "assets"

    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets"
        )


# ============================================================
# DATABASE STARTUP
# ============================================================

@app.on_event("startup")
def startup():
    init_db()


# ============================================================
# REQUEST MODELS
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class DecisionRequest(BaseModel):
    decision: str
    note: str = ""


class ChatRequest(BaseModel):
    message: str
    transaction_id: str | None = None


class SettingsRequest(BaseModel):
    alert_threshold: int = 75
    auto_route_escalations: bool = True
    daily_review_limit: int = 50
    analyst_email: str = "analyst@fraudguard.ai"
    notifications_enabled: bool = True
    max_velocity_10m: int = 3
    block_new_beneficiaries: bool = False
    risk_propagation_enabled: bool = True
    auto_create_cases: bool = True
    retention_days: int = 365


class WorkflowDecisionRequest(BaseModel):
    decision: str
    note: str = ""


class DemoScenarioRequest(BaseModel):
    customer_id: str = "C101"


DEFAULT_SETTINGS = {
    "alert_threshold": 75,
    "auto_route_escalations": True,
    "daily_review_limit": 50,
    "analyst_email": "analyst@fraudguard.ai",
    "notifications_enabled": True,
    "max_velocity_10m": 3,
    "block_new_beneficiaries": False,
    "risk_propagation_enabled": True,
    "auto_create_cases": True,
    "retention_days": 365,
}


# ============================================================
# FRONTEND HOME
# ============================================================

@app.get("/", include_in_schema=False)
def home():
    index_file = FRONTEND / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "React frontend build not found. "
                "Run 'npm run build' inside frontend-react."
            )
        )

    return FileResponse(index_file)


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/login")
def login(req: LoginRequest):

    username = (req.username or "").strip().lower()
    email = username

    if "@" in username:
        email = username
        username = username.split("@", 1)[0]

    db = get_db()
    try:
        user = db.execute(
            "SELECT id,email,role,permissions FROM users WHERE (id=? OR email=?) AND active=1",
            (username, email),
        ).fetchone()
    finally:
        db.close()

    if user and req.password == "demo123":
        return {
            "success": True,
            "user": {
                "username": user["id"],
                "email": user["email"],
                "role": user["role"],
                "permissions": json.loads(user["permissions"]),
            }
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid demo credentials"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    db = get_db()

    try:
        total = db.execute(
            "SELECT COUNT(*) c FROM transactions"
        ).fetchone()["c"]

        suspicious = db.execute(
            "SELECT COUNT(*) c FROM transactions "
            "WHERE risk_score >= 50"
        ).fetchone()["c"]

        high = db.execute(
            "SELECT COUNT(*) c FROM transactions "
            "WHERE risk_score >= 75"
        ).fetchone()["c"]

        confirmed = db.execute(
            "SELECT COUNT(*) c FROM cases "
            "WHERE status='Confirmed Fraud'"
        ).fetchone()["c"]

        under_review = db.execute(
            "SELECT COUNT(*) c FROM cases "
            "WHERE status IN "
            "('New','Under Investigation','Escalated')"
        ).fetchone()["c"]

        risk = [
            dict(r)
            for r in db.execute(
                """
                SELECT
                    CASE
                        WHEN risk_score >= 75 THEN 'High'
                        WHEN risk_score >= 50 THEN 'Medium'
                        ELSE 'Low'
                    END risk,
                    COUNT(*) count
                FROM transactions
                GROUP BY risk
                """
            ).fetchall()
        ]

        locations = [
            dict(r)
            for r in db.execute(
                """
                SELECT location, COUNT(*) count
                FROM transactions
                WHERE risk_score >= 50
                GROUP BY location
                ORDER BY count DESC
                LIMIT 8
                """
            ).fetchall()
        ]

        merchants = [
            dict(r)
            for r in db.execute(
                """
                SELECT merchant_category, COUNT(*) count
                FROM transactions
                WHERE risk_score >= 50
                GROUP BY merchant_category
                ORDER BY count DESC
                LIMIT 8
                """
            ).fetchall()
        ]

        return {
            "kpis": {
                "total": total,
                "suspicious": suspicious,
                "high_risk": high,
                "confirmed_fraud": confirmed,
                "under_review": under_review
            },
            "risk_distribution": risk,
            "risk_locations": locations,
            "risk_merchants": merchants
        }

    finally:
        db.close()


# ============================================================
# TRANSACTIONS
# ============================================================

@app.get("/api/transactions")
def transactions(
    q: str = "",
    risk: str = "all",
    status: str = "all"
):

    db = get_db()

    try:
        where = ["1=1"]
        params = []

        if q:
            where.append(
                "(t.id LIKE ? "
                "OR t.customer_id LIKE ? "
                "OR c.name LIKE ? "
                "OR t.merchant_category LIKE ?)"
            )

            params += [f"%{q}%"] * 4

        if risk != "all":

            bounds = {
                "low": (0, 49),
                "medium": (50, 74),
                "high": (75, 100)
            }

            lo, hi = bounds.get(
                risk,
                (0, 100)
            )

            where.append(
                "t.risk_score BETWEEN ? AND ?"
            )

            params += [lo, hi]

        if status != "all":
            where.append("t.status=?")
            params.append(status)

        rows = db.execute(
            f"""
            SELECT
                t.*,
                c.name customer_name
            FROM transactions t
            JOIN customers c
                ON c.id=t.customer_id
            WHERE {' AND '.join(where)}
            ORDER BY
                t.risk_score DESC,
                t.timestamp DESC
            """,
            params
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        db.close()


# ============================================================
# TRANSACTION DETAIL
# ============================================================

@app.get("/api/transactions/{transaction_id}")
def transaction_detail(transaction_id: str):

    db = get_db()

    try:
        row = db.execute(
            """
            SELECT
                t.*,
                c.name customer_name,
                c.avg_amount,
                c.max_amount,
                c.normal_locations,
                c.normal_merchants,
                c.disputes,
                c.prior_flags,
                c.account_age_days
            FROM transactions t
            JOIN customers c
                ON c.id=t.customer_id
            WHERE t.id=?
            """,
            (transaction_id,)
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        return dict(row)

    finally:
        db.close()


# ============================================================
# AI INVESTIGATION
# ============================================================

@app.post("/api/investigate/{transaction_id}")
def investigate(transaction_id: str):

    result = investigate_transaction(transaction_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return result


# ============================================================
# INVESTIGATION EVIDENCE
# ============================================================

@app.get("/api/investigations/{transaction_id}/evidence")
def investigation_evidence(transaction_id: str):

    result = investigate_transaction(transaction_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db = get_db()
    try:
        vault = [dict(row) for row in db.execute("SELECT * FROM evidence_vault WHERE transaction_id=? ORDER BY created_at DESC", (transaction_id,)).fetchall()]
    finally:
        db.close()

    return {
        "transaction_id": transaction_id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "evidence": result["evidence"],
        "evidence_vault": vault,
        "agent_trace": result["audit"]["trace"]
    }


@app.get("/api/workflow/{transaction_id}")
def workflow(transaction_id: str):
    """Return the complete transaction-to-case investigation workflow."""
    result = investigate_transaction(transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    customer_id = result["transaction"]["customer_id"]
    db = get_db()
    try:
        timeline = [dict(row) for row in db.execute(
            "SELECT id, amount, currency, timestamp, location, merchant_category, risk_score, status FROM transactions WHERE customer_id=? ORDER BY timestamp ASC",
            (customer_id,),
        ).fetchall()]
        vault = [dict(row) for row in db.execute(
            "SELECT * FROM evidence_vault WHERE transaction_id=? ORDER BY created_at DESC",
            (transaction_id,),
        ).fetchall()]
        case = db.execute("SELECT * FROM cases WHERE id=?", (result["case_id"],)).fetchone()
    finally:
        db.close()

    return {
        "transaction": result["transaction"],
        "risk": {"score": result["risk_score"], "level": result["risk_level"], "confidence": result["confidence"]},
        "anomaly_detection": result["anomaly_detection"],
        "typologies": result["typologies"],
        "explanation": {"evidence": result["evidence"], "breakdown": result["agents"]["risk_scoring"]["breakdown"]},
        "customer": {"id": customer_id, "name": result["transaction"]["customer_name"]},
        "timeline": timeline,
        "network": result["agents"]["network_intelligence"],
        "copilot": {"recommendation": result["recommendation"], "case_id": result["case_id"]},
        "case": dict(case) if case else None,
        "evidence_vault": vault,
        "audit_trace": result["audit"]["trace"],
    }


@app.get("/api/transactions/{transaction_id}/timeline")
def transaction_timeline(transaction_id: str):
    db = get_db()
    try:
        row = db.execute("SELECT customer_id FROM transactions WHERE id=?", (transaction_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return [dict(item) for item in db.execute(
            "SELECT id, amount, currency, timestamp, location, merchant_category, risk_score, status FROM transactions WHERE customer_id=? ORDER BY timestamp ASC",
            (row["customer_id"],),
        ).fetchall()]
    finally:
        db.close()


@app.get("/api/evidence-vault/{transaction_id}")
def evidence_vault(transaction_id: str):
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM transactions WHERE id=?", (transaction_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Transaction not found")
        return [dict(row) for row in db.execute("SELECT * FROM evidence_vault WHERE transaction_id=? ORDER BY created_at DESC", (transaction_id,)).fetchall()]
    finally:
        db.close()


# ============================================================
# CASES
# ============================================================

@app.get("/api/cases")
def cases():

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT *
            FROM cases
            ORDER BY created_at DESC
            """
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        db.close()


# ============================================================
# CASE DECISION
# ============================================================

@app.post("/api/cases/{case_id}/decision")
def decision(
    case_id: str,
    req: DecisionRequest
):

    allowed = {
        "approve": "Cleared",
        "reject": "Confirmed Fraud",
        "escalate": "Escalated",
        "confirm_suspicious": "Confirmed Fraud",
        "false_positive": "False Positive",
        "close_case": "Resolved"
    }

    if req.decision not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be approve, "
                "reject, or escalate"
            )
        )

    db = get_db()

    try:
        row = db.execute(
            "SELECT * FROM cases WHERE id=?",
            (case_id,)
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Case not found"
            )

        new_status = allowed[req.decision]

        if (
            req.decision in {"reject", "escalate", "confirm_suspicious"}
            and not req.note.strip()
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "A note is required for "
                    "reject or escalate decisions"
                )
            )

        db.execute(
            """
            UPDATE cases
            SET
                status=?,
                analyst_note=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                new_status,
                req.note.strip(),
                case_id
            )
        )

        db.execute(
            """
            INSERT INTO audit_log(
                action,
                entity_id,
                details
            )
            VALUES(?,?,?)
            """,
            (
                "ANALYST_DECISION",
                case_id,
                json.dumps({
                    "decision": req.decision,
                    "note": req.note.strip(),
                    "human_in_loop": True
                })
            )
        )

        db.commit()

        return {
            "success": True,
            "status": new_status
        }

    finally:
        db.close()


# ============================================================
# ALERTS
# ============================================================

@app.get("/api/alerts")
def alerts():

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT
                'High-risk transaction' type,
                id transaction_id,
                customer_id,
                amount,
                risk_score,
                timestamp,
                location,
                CASE
                    WHEN risk_score >= 90 THEN 'CRITICAL'
                    WHEN risk_score >= 75 THEN 'HIGH'
                    WHEN risk_score >= 50 THEN 'MEDIUM'
                    ELSE 'LOW'
                END priority
            FROM transactions
            WHERE risk_score >= 50
            ORDER BY timestamp DESC
            LIMIT 20
            """
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        db.close()


@app.get("/api/alerts/summary")
def alert_summary():
    db = get_db()
    try:
        rows = db.execute("""
            SELECT CASE WHEN risk_score >= 90 THEN 'CRITICAL'
                        WHEN risk_score >= 75 THEN 'HIGH'
                        WHEN risk_score >= 50 THEN 'MEDIUM'
                        ELSE 'LOW' END priority, COUNT(*) count
            FROM transactions WHERE risk_score >= 50 GROUP BY priority
        """).fetchall()
        counts = {row["priority"]: row["count"] for row in rows}
        return {priority: counts.get(priority, 0) for priority in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    finally:
        db.close()


# ============================================================
# AUDIT LOG
# ============================================================

@app.get("/api/audit")
def audit():

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT *
            FROM audit_log
            ORDER BY created_at DESC
            LIMIT 100
            """
        ).fetchall()

        return [dict(r) for r in rows]

    finally:
        db.close()


# ============================================================
# CUSTOMER NETWORK
# ============================================================

@app.get("/api/network/risk-propagation")
def network_risk_propagation_live():
    db = get_db()
    try:
        rows = db.execute("""
            SELECT c.id, c.name, COALESCE(AVG(t.risk_score), 0) direct_risk,
                   COUNT(DISTINCT f.source_customer_id) + COUNT(DISTINCT f.target_customer_id) connected_edges
            FROM customers c
            LEFT JOIN transactions t ON t.customer_id=c.id
            LEFT JOIN fund_transfers f ON f.source_customer_id=c.id OR f.target_customer_id=c.id
            GROUP BY c.id, c.name
            ORDER BY direct_risk DESC
        """).fetchall()
        return [{
            "customer_id": row["id"], "name": row["name"],
            "direct_risk": round(float(row["direct_risk"]), 1),
            "connected_edges": row["connected_edges"],
            "propagated_risk": round(min(100, float(row["direct_risk"]) + min(20, row["connected_edges"] * 4)), 1),
            "reason": "Network exposure increases review priority" if row["connected_edges"] else "No connected transfer exposure",
        } for row in rows]
    finally:
        db.close()

@app.get("/api/network/{customer_id}")
def network(customer_id: str):

    db = get_db()

    try:
        c = db.execute(
            """
            SELECT *
            FROM customers
            WHERE id=?
            """,
            (customer_id,)
        ).fetchone()

        if not c:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        tx = db.execute(
            """
            SELECT *
            FROM transactions
            WHERE customer_id=?
            ORDER BY timestamp DESC
            """,
            (customer_id,)
        ).fetchall()

        nodes = [
            {
                "id": customer_id,
                "type": "customer",
                "label": c["name"]
            }
        ]

        edges = []
        seen = set()

        for t in tx:

            related_entities = [
                ("device", t["device_id"]),
                ("ip", t["ip_address"]),
                ("merchant", t["merchant_category"]),
                ("location", t["location"])
            ]

            for typ, val in related_entities:

                nid = f"{typ}:{val}"

                if nid not in seen:
                    seen.add(nid)

                    nodes.append({
                        "id": nid,
                        "type": typ,
                        "label": str(val)
                    })

                edges.append({
                    "source": customer_id,
                    "target": nid,
                    "transaction": t["id"]
                })

        transfers = db.execute("""
            SELECT source_customer_id, target_customer_id, amount, beneficiary
            FROM fund_transfers
            WHERE source_customer_id=? OR target_customer_id=?
        """, (customer_id, customer_id)).fetchall()
        for transfer in transfers:
            target = transfer["target_customer_id"] if transfer["source_customer_id"] == customer_id else transfer["source_customer_id"]
            target_node = f"customer:{target}"
            if target_node not in seen:
                seen.add(target_node)
                connected = db.execute("SELECT name FROM customers WHERE id=?", (target,)).fetchone()
                nodes.append({"id": target_node, "type": "customer", "label": f"{target} / {connected['name'] if connected else target}"})
            edges.append({"source": customer_id, "target": target_node, "relationship": "fund_transfer", "amount": transfer["amount"], "beneficiary": transfer["beneficiary"]})

        return {
            "nodes": nodes,
            "edges": edges
        }

    finally:
        db.close()


# ============================================================
# AI CHAT
# ============================================================

@app.post("/api/chat")
def chat(req: ChatRequest):

    msg = (req.message or "").lower().strip()

    if not msg:
        raise HTTPException(
            status_code=400,
            detail="Message is required"
        )

    if req.transaction_id:

        result = investigate_transaction(
            req.transaction_id
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        reasons = [
            e["explanation"]
            for e in result["evidence"][:5]
        ]

        if "why" in msg or "risk" in msg:

            return {
                "answer": (
                    f"This transaction is "
                    f"{result['risk_level']} risk "
                    f"with {result['confidence']}% confidence. "
                    + " ".join(reasons)
                )
            }

        if "evidence" in msg:

            return {
                "answer": (
                    "Strongest evidence: "
                    + " | ".join(reasons[:3])
                )
            }

        if "recommend" in msg or "action" in msg:

            return {
                "answer": (
                    f"Recommended action: {result['recommendation']}. "
                    f"Case {result['case_id']} should be reviewed by the analyst immediately."
                )
            }

        return {
            "answer": (
                f"Case {result['case_id']} has a "
                f"{result['risk_level']} risk assessment. "
                f"Recommended action: "
                f"{result['recommendation']}."
            )
        }

    default_answer = (
        "I can explain transaction risk, "
        "summarize evidence, suggest investigation "
        "steps, and answer questions about the "
        "fraud-policy knowledge base."
    )

    if any(term in msg for term in ("flow", "layering", "money laundering", "pass-through")):
        db = get_db()
        try:
            flow = db.execute("SELECT COUNT(*) count, COALESCE(SUM(amount), 0) total FROM fund_transfers").fetchone()
            transfers = db.execute("SELECT source_customer_id, target_customer_id FROM fund_transfers").fetchall()
            graph = {}
            for transfer in transfers:
                graph.setdefault(transfer["source_customer_id"], set()).add(transfer["target_customer_id"])

            def reaches_cycle(start, node, visited):
                if node == start and visited:
                    return True
                if node in visited:
                    return False
                return any(reaches_cycle(start, target, visited | {node}) for target in graph.get(node, set()))

            loop = sum(1 for start in graph if reaches_cycle(start, start, set()))
            return {"answer": f"The live fund-flow graph contains {flow['count']} transfers totaling ₹{float(flow['total']):,.0f}. It shows {loop} circular flow pattern(s), consistent with possible layering or pass-through activity requiring enhanced investigation."}
        finally:
            db.close()

    if any(term in msg for term in ("login", "session", "sim", "takeover", "beneficiary")):
        db = get_db()
        try:
            events = db.execute("SELECT event_type, details FROM activity_events ORDER BY event_time DESC LIMIT 5").fetchall()
            if events:
                return {"answer": "Recent account/session signals: " + "; ".join(f"{event['event_type']}: {event['details']}" for event in events) + ". These signals should be correlated with device, IP and transaction behavior before closing the case."}
        finally:
            db.close()

    if any(term in msg for term in ("connected accounts", "risk propagation", "network exposure")):
        db = get_db()
        try:
            row = db.execute("""
                SELECT c.id, c.name, AVG(t.risk_score) direct_risk
                FROM customers c JOIN transactions t ON t.customer_id=c.id
                GROUP BY c.id, c.name ORDER BY direct_risk DESC LIMIT 1
            """).fetchone()
            if row:
                return {"answer": f"{row['name']} ({row['id']}) currently has the highest direct customer risk at {float(row['direct_risk']):.1f}. Network-connected entities should be reviewed because risk can propagate through shared devices, IPs and fund-transfer relationships."}
        finally:
            db.close()

    if "risk" in msg or "fraud" in msg:
        db = get_db()
        try:
            high_risk = db.execute(
                "SELECT id, risk_score, customer_id, location FROM transactions WHERE risk_score >= 75 ORDER BY risk_score DESC LIMIT 1"
            ).fetchone()
            if high_risk:
                return {
                    "answer": (
                        f"The highest-risk live transaction is {high_risk['id']} for customer {high_risk['customer_id']} at {high_risk['location']}. "
                        f"Its risk score is {high_risk['risk_score']} and it should be escalated for review."
                    )
                }
        finally:
            db.close()

    return {"answer": default_answer}


@app.get("/api/settings")
def get_settings():
    db = get_db()
    try:
        row = db.execute(
            "SELECT value FROM settings WHERE key='fraudguard'"
        ).fetchone()
        if row:
            return json.loads(row["value"])
        return DEFAULT_SETTINGS.copy()
    finally:
        db.close()


@app.post("/api/settings")
def save_settings(req: SettingsRequest):
    payload = {
        "alert_threshold": req.alert_threshold,
        "auto_route_escalations": req.auto_route_escalations,
        "daily_review_limit": req.daily_review_limit,
        "analyst_email": req.analyst_email,
        "notifications_enabled": req.notifications_enabled,
        "max_velocity_10m": req.max_velocity_10m,
        "block_new_beneficiaries": req.block_new_beneficiaries,
        "risk_propagation_enabled": req.risk_propagation_enabled,
        "auto_create_cases": req.auto_create_cases,
        "retention_days": req.retention_days,
    }

    db = get_db()
    try:
        db.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("fraudguard", json.dumps(payload))
        )
        db.commit()
        return payload
    finally:
        db.close()


# ============================================================
# EXPORT TRANSACTIONS CSV
# ============================================================

@app.get("/api/export/transactions.csv")
def export_csv():

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT *
            FROM transactions
            ORDER BY timestamp DESC
            """
        ).fetchall()

        out = io.StringIO()

        writer = csv.writer(out)

        writer.writerow(
            rows[0].keys()
            if rows
            else ["id"]
        )

        for row in rows:
            writer.writerow(list(row))

        return StreamingResponse(
            iter([out.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition":
                    "attachment; "
                    "filename=transactions.csv"
            }
        )

    finally:
        db.close()


# ============================================================
# PDF REPORT
# ============================================================

@app.get("/api/reports/{transaction_id}.pdf")
def report_pdf(transaction_id: str):

    result = investigate_transaction(
        transaction_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    reports_dir = BASE / "data" / "reports"

    path = make_report(
        result,
        reports_dir
    )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=Path(path).name
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    db = get_db()

    try:
        counts = {}

        for table in (
            "customers",
            "transactions",
            "cases",
            "audit_log"
        ):
            counts[table] = db.execute(
                f"SELECT COUNT(*) c FROM {table}"
            ).fetchone()["c"]

        return {
            "status": "ok",
            "database": (
                "postgresql"
                if getattr(db, "postgres", False)
                else "sqlite"
            ),
            "counts": counts
        }

    finally:
        db.close()


# ============================================================
# FRAUD RINGS
# ============================================================

@app.get("/api/fraud-rings")
def fraud_rings(
    min_links: int = Query(
        2,
        ge=1,
        le=20
    )
):

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT
                device_id,
                ip_address,
                COUNT(DISTINCT customer_id)
                    customer_count,
                COUNT(*)
                    transaction_count,
                SUM(
                    CASE
                        WHEN risk_score >= 75
                        THEN 1
                        ELSE 0
                    END
                ) high_risk_count

            FROM transactions

            GROUP BY
                device_id,
                ip_address

            HAVING
                COUNT(DISTINCT customer_id) >= ?

            ORDER BY
                customer_count DESC,
                high_risk_count DESC
            """,
            (min_links,)
        ).fetchall()

        rings = []

        for i, row in enumerate(rows, 1):

            members = db.execute(
                """
                SELECT DISTINCT customer_id
                FROM transactions
                WHERE
                    device_id=?
                    AND ip_address=?
                """,
                (
                    row["device_id"],
                    row["ip_address"]
                )
            ).fetchall()

            rings.append({
                "ring_id": f"RING-{i:03d}",
                "device_id": row["device_id"],
                "ip_address": row["ip_address"],
                "customer_count": row["customer_count"],
                "transaction_count": row["transaction_count"],
                "high_risk_count": row["high_risk_count"],
                "members": [
                    x["customer_id"]
                    for x in members
                ]
            })

        return rings

    finally:
        db.close()


# ============================================================
# CUSTOMER RISK PROFILE
# ============================================================

@app.get("/api/customers/{customer_id}/risk-profile")
def customer_risk_profile(customer_id: str):

    db = get_db()

    try:
        customer = db.execute(
            """
            SELECT *
            FROM customers
            WHERE id=?
            """,
            (customer_id,)
        ).fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        transactions = db.execute(
            """
            SELECT *
            FROM transactions
            WHERE customer_id=?
            ORDER BY timestamp DESC
            """,
            (customer_id,)
        ).fetchall()

        if not transactions:

            return {
                "customer": dict(customer),
                "risk_score": 0,
                "transaction_count": 0,
                "high_risk_count": 0,
                "patterns": []
            }

        avg = (
            sum(
                float(t["risk_score"] or 0)
                for t in transactions
            )
            / len(transactions)
        )

        high = sum(
            1
            for t in transactions
            if float(t["risk_score"] or 0) >= 75
        )

        patterns = []

        if high:
            patterns.append(
                "High-risk transaction history"
            )

        if any(
            t["device_id"] != "DEV-A"
            for t in transactions
        ):
            patterns.append(
                "Non-baseline device usage"
            )

        if len({
            t["ip_address"]
            for t in transactions
        }) > 1:
            patterns.append(
                "Multiple IP fingerprints"
            )

        return {
            "customer": dict(customer),
            "risk_score": round(
                min(100, avg + high * 5),
                1
            ),
            "transaction_count": len(transactions),
            "high_risk_count": high,
            "patterns": patterns
        }

    finally:
        db.close()


@app.get("/api/customers/{customer_id}/baseline")
def customer_baseline(customer_id: str):
    db = get_db()
    try:
        customer = db.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        transactions = db.execute("SELECT * FROM transactions WHERE customer_id=? ORDER BY timestamp", (customer_id,)).fetchall()
        if not transactions:
            return {"customer_id": customer_id, "transaction_count": 0, "average_amount": 0, "transactions_per_day": 0, "usual_locations": [], "usual_devices": [], "common_beneficiaries": []}
        timestamps = [datetime.datetime.fromisoformat(row["timestamp"]) for row in transactions]
        span_days = max(1, (timestamps[-1] - timestamps[0]).total_seconds() / 86400)
        beneficiaries = db.execute("SELECT beneficiary, COUNT(*) count FROM fund_transfers WHERE source_customer_id=? GROUP BY beneficiary ORDER BY count DESC", (customer_id,)).fetchall()
        return {
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "transaction_count": len(transactions),
            "average_amount": round(sum(float(row["amount"]) for row in transactions) / len(transactions), 2),
            "transactions_per_day": round(len(transactions) / span_days, 2),
            "usual_locations": [row["location"] for row in db.execute("SELECT location, COUNT(*) count FROM transactions WHERE customer_id=? GROUP BY location ORDER BY count DESC LIMIT 5", (customer_id,)).fetchall()],
            "usual_devices": [row["device_id"] for row in db.execute("SELECT device_id, COUNT(*) count FROM transactions WHERE customer_id=? GROUP BY device_id ORDER BY count DESC LIMIT 5", (customer_id,)).fetchall()],
            "common_beneficiaries": [dict(row) for row in beneficiaries],
            "comparison": {"configured_average": customer["avg_amount"], "configured_locations": customer["normal_locations"]},
        }
    finally:
        db.close()


@app.get("/api/customers/{customer_id}/risk-evolution")
def customer_risk_evolution(customer_id: str):
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (customer_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        rows = db.execute("SELECT timestamp, risk_score FROM transactions WHERE customer_id=? ORDER BY timestamp", (customer_id,)).fetchall()
        points = [{"label": f"Event {index + 1}", "timestamp": row["timestamp"], "risk_score": round(float(row["risk_score"] or 0), 1)} for index, row in enumerate(rows)]
        return {"customer_id": customer_id, "points": points, "trend": "RISING" if len(points) > 1 and points[-1]["risk_score"] > points[0]["risk_score"] else "STABLE"}
    finally:
        db.close()


@app.get("/api/customers")
def customers():
    db = get_db()
    try:
        rows = db.execute("""
            SELECT c.id, c.name, c.account_age_days,
                   COUNT(t.id) transaction_count,
                   COALESCE(AVG(t.risk_score), 0) risk_score,
                   SUM(CASE WHEN t.risk_score >= 75 THEN 1 ELSE 0 END) high_risk_count
            FROM customers c
            LEFT JOIN transactions t ON t.customer_id=c.id
            GROUP BY c.id, c.name, c.account_age_days
            ORDER BY risk_score DESC
        """).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


@app.get("/api/merchants")
def merchants():
    db = get_db()
    try:
        rows = db.execute("""
            SELECT merchant_category merchant, COUNT(*) transaction_count,
                   COALESCE(AVG(risk_score), 0) risk_score,
                   SUM(CASE WHEN risk_score >= 75 THEN 1 ELSE 0 END) high_risk_count,
                   COALESCE(SUM(amount), 0) total_amount
            FROM transactions
            GROUP BY merchant_category
            ORDER BY risk_score DESC, transaction_count DESC
        """).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


@app.get("/api/reports")
def reports():
    db = get_db()
    try:
        rows = db.execute("""
            SELECT 'INV-' || substr(t.id, 5) report_id, t.id transaction_id,
                   t.customer_id, t.risk_score, t.status, t.timestamp generated_at
            FROM transactions t
            WHERE t.risk_score >= 50
            ORDER BY t.timestamp DESC
            LIMIT 50
        """).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


@app.post("/api/demo-scenarios/{scenario}")
def demo_scenario(scenario: str, req: DemoScenarioRequest):
    scenarios = {
        "account-takeover": ("LOGIN_ANOMALY", "New device, new IP, new location and high-value transfer", 180000, "Mumbai", "DEV-SCENARIO-X", "198.51.100.42"),
        "mule-account": ("PASS_THROUGH_PATTERN", "Rapid inbound and outbound movement across connected accounts", 92000, "Delhi", "DEV-MULE-01", "203.0.113.10"),
        "fraud-ring": ("SHARED_FINGERPRINT", "Customer linked to a known device and IP cluster", 125000, "Dubai", "DEV-RING-DEMO", "203.0.113.20"),
        "structuring": ("STRUCTURING_PATTERN", "Repeated transfers below a reporting threshold", 9900, "Bengaluru", "DEV-A", "10.0.0.1"),
        "suspicious-beneficiary": ("NEW_BENEFICIARY", "New beneficiary followed by an unusual payment", 145000, "Chennai", "DEV-BENEFICIARY", "198.51.100.55"),
    }
    if scenario not in scenarios:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario}")
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (req.customer_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        event_type, details, amount, location, device, ip = scenarios[scenario]
        now = datetime.datetime.now().isoformat(timespec="seconds")
        transaction_id = f"DEMO-{scenario.upper().replace('-', '')}-{datetime.datetime.now().strftime('%H%M%S')}"
        db.execute("INSERT INTO transactions(id,customer_id,amount,currency,timestamp,location,merchant_category,payment_method,device_id,ip_address,risk_score,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (transaction_id, req.customer_id, amount, "INR", now, location, "Electronics", "Card", device, ip, 0, "New"))
        db.execute("INSERT INTO activity_events(customer_id,event_type,details,event_time,risk_signal) VALUES(?,?,?,?,?)", (req.customer_id, event_type, details, now, 1.0))
        db.execute("INSERT INTO audit_log(action,entity_id,details) VALUES(?,?,?)", ("DEMO_SCENARIO_CREATED", transaction_id, json.dumps({"scenario": scenario, "customer_id": req.customer_id})))
        db.commit()
    finally:
        db.close()
    from .agents import compute_score_only
    score = compute_score_only(transaction_id)
    db = get_db()
    try:
        db.execute("UPDATE transactions SET risk_score=? WHERE id=?", (score, transaction_id))
        db.commit()
    finally:
        db.close()
    return {"scenario": scenario, "transaction_id": transaction_id, "risk_score": score, "investigation_url": f"/api/workflow/{transaction_id}"}


@app.get("/api/customers/{customer_id}/activity")
def customer_activity(customer_id: str):
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (customer_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        rows = db.execute("SELECT * FROM activity_events WHERE customer_id=? ORDER BY event_time DESC", (customer_id,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


@app.get("/api/fund-flows/{customer_id}")
def fund_flows(customer_id: str):
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM customers WHERE id=?", (customer_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        rows = [dict(row) for row in db.execute("""
            SELECT f.*, s.name source_name, t.name target_name
            FROM fund_transfers f
            JOIN customers s ON s.id=f.source_customer_id
            JOIN customers t ON t.id=f.target_customer_id
            ORDER BY f.transfer_time ASC
        """).fetchall()]
        graph = {}
        for row in rows:
            graph.setdefault(row["source_customer_id"], set()).add(row["target_customer_id"])

        def reaches_cycle(start, node, visited):
            if node == start and visited:
                return True
            if node in visited:
                return False
            return any(reaches_cycle(start, target, visited | {node}) for target in graph.get(node, set()))

        circular = any(reaches_cycle(start, start, set()) for start in graph)
        return {
            "customer_id": customer_id,
            "transfers": rows,
            "total_value": round(sum(float(row["amount"]) for row in rows), 2),
            "entity_count": len(set([customer_id] + [row["source_customer_id"] for row in rows] + [row["target_customer_id"] for row in rows])),
            "circular_flow_detected": circular,
            "risk_reason": "Circular or pass-through movement detected" if circular else "No circular flow detected",
        }
    finally:
        db.close()


# ============================================================
# SPA FALLBACK
# ============================================================

# This is useful if your React application uses
# client-side routes such as /dashboard, /transactions,
# /cases, etc.
#
# API routes are defined above, so they will continue
# to work normally.

@app.get("/{full_path:path}", include_in_schema=False)
def react_spa_fallback(full_path: str):

    # Never treat API URLs as frontend routes.
    if full_path.startswith("api/"):
        raise HTTPException(
            status_code=404,
            detail="API endpoint not found"
        )

    index_file = FRONTEND / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "React frontend build not found. "
                "Run 'npm run build' inside frontend-react."
            )
        )

    return FileResponse(index_file)
