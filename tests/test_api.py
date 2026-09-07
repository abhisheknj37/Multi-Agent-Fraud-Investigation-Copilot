import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
os.environ['DATABASE_URL']=''
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db
init_db()

client=TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_transactions():
    r=client.get('/api/transactions'); assert r.status_code==200; assert len(r.json())>=15

def test_investigation():
    r=client.post('/api/investigate/TXN1003'); assert r.status_code==200
    body=r.json(); assert body['risk_level'] in {'HIGH','MEDIUM','LOW'}; assert body['evidence']

def test_fraud_rings_endpoint():
    r=client.get('/api/fraud-rings'); assert r.status_code==200; assert isinstance(r.json(),list)

def test_missing_transaction():
    assert client.post('/api/investigate/NOPE').status_code==404

def test_unified_workflow_contains_all_stages():
    r = client.get('/api/workflow/TXN1003')
    assert r.status_code == 200
    body = r.json()
    assert body['risk']['score'] >= 0
    assert body['anomaly_detection']['detected'] is True
    assert 'explanation' in body
    assert 'timeline' in body and body['timeline']
    assert 'case' in body
    assert 'audit_trace' in body

def test_timeline_and_evidence_vault():
    timeline = client.get('/api/transactions/TXN1003/timeline')
    vault = client.get('/api/evidence-vault/TXN1003')
    assert timeline.status_code == 200 and len(timeline.json()) >= 1
    assert vault.status_code == 200 and len(vault.json()) >= 1

def test_login_returns_analyst_role():
    r = client.post('/api/login', json={'username': 'analyst@fraudguard.ai', 'password': 'demo123'})
    assert r.status_code == 200
    assert r.json()['user']['role'] == 'Fraud Analyst'
    assert 'investigate' in r.json()['user']['permissions']

def test_enterprise_workspace_data_endpoints():
    customers = client.get('/api/customers')
    merchants = client.get('/api/merchants')
    reports = client.get('/api/reports')
    assert customers.status_code == 200 and customers.json()
    assert merchants.status_code == 200 and merchants.json()
    assert reports.status_code == 200 and reports.json()

def test_aml_fund_flow_and_account_events():
    flows = client.get('/api/fund-flows/C101')
    events = client.get('/api/customers/C101/activity')
    propagation = client.get('/api/network/risk-propagation')
    assert flows.status_code == 200
    assert flows.json()['transfers'] and flows.json()['circular_flow_detected'] is True
    assert events.status_code == 200 and any(item['event_type'] == 'LOGIN_ANOMALY' for item in events.json())
    assert propagation.status_code == 200 and propagation.json()

def test_copilot_answers_aml_question():
    r = client.post('/api/chat', json={'message': 'Show me possible money laundering fund flows'})
    assert r.status_code == 200
    assert 'fund-flow' in r.json()['answer']

def test_behavioral_baseline_and_risk_evolution():
    baseline = client.get('/api/customers/C101/baseline')
    evolution = client.get('/api/customers/C101/risk-evolution')
    assert baseline.status_code == 200
    assert baseline.json()['average_amount'] > 0
    assert baseline.json()['usual_locations']
    assert evolution.status_code == 200 and evolution.json()['points']

def test_alert_prioritization_and_demo_scenario():
    summary = client.get('/api/alerts/summary')
    scenario = client.post('/api/demo-scenarios/account-takeover', json={'customer_id': 'C101'})
    assert summary.status_code == 200
    assert set(summary.json()) == {'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'}
    assert scenario.status_code == 200 and scenario.json()['transaction_id'].startswith('DEMO-')

def test_extended_settings_persist():
    payload = {
        'alert_threshold': 80,
        'auto_route_escalations': True,
        'daily_review_limit': 40,
        'analyst_email': 'analyst@fraudguard.ai',
        'notifications_enabled': True,
        'max_velocity_10m': 5,
        'block_new_beneficiaries': True,
        'risk_propagation_enabled': False,
        'auto_create_cases': True,
        'retention_days': 730,
    }
    saved = client.post('/api/settings', json=payload)
    loaded = client.get('/api/settings')
    assert saved.status_code == 200
    assert loaded.json()['max_velocity_10m'] == 5
    assert loaded.json()['block_new_beneficiaries'] is True
    assert loaded.json()['retention_days'] == 730
