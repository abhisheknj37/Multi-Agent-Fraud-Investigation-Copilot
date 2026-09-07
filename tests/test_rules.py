import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.agents import compute_score_only
from app.db import init_db
init_db()

def test_known_high_risk_transaction():
    assert compute_score_only('TXN1003') >= 50

def test_normal_transaction_lower_than_high_risk():
    assert compute_score_only('TXN1001') < compute_score_only('TXN1003')
