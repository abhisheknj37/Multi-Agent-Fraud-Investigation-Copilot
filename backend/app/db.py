import os, sqlite3, datetime, json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / 'data' / 'fraud.db'
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

class DB:
    def __init__(self, conn, postgres=False):
        self.conn = conn
        self.postgres = postgres
    def execute(self, sql, params=()):
        if self.postgres:
            sql = sql.replace('?', '%s')
        return self.conn.execute(sql, params)
    def executemany(self, sql, params):
        if self.postgres:
            sql = sql.replace('?', '%s')
        return self.conn.executemany(sql, params)
    def executescript(self, script):
        if self.postgres:
            for statement in script.split(';'):
                statement = statement.strip()
                if statement:
                    self.conn.execute(statement)
        else:
            self.conn.executescript(script)
    def commit(self): self.conn.commit()
    def close(self): self.conn.close()

def get_db():
    if DATABASE_URL.startswith('postgresql'):
        import psycopg
        from psycopg.rows import dict_row
        return DB(psycopg.connect(DATABASE_URL, row_factory=dict_row), True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return DB(db, False)

def init_db():
    db = get_db()
    if db.postgres:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS customers(id TEXT PRIMARY KEY,name TEXT,avg_amount DOUBLE PRECISION,max_amount DOUBLE PRECISION,normal_locations TEXT,normal_merchants TEXT,disputes INTEGER,prior_flags INTEGER,account_age_days INTEGER);
        CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY,customer_id TEXT REFERENCES customers(id),amount DOUBLE PRECISION,currency TEXT,timestamp TEXT,location TEXT,merchant_category TEXT,payment_method TEXT,device_id TEXT,ip_address TEXT,risk_score DOUBLE PRECISION,status TEXT DEFAULT 'New');
        CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,transaction_id TEXT REFERENCES transactions(id),status TEXT,assigned_analyst TEXT,analyst_note TEXT,created_at TEXT,updated_at TEXT);
        CREATE TABLE IF NOT EXISTS audit_log(id SERIAL PRIMARY KEY,action TEXT,entity_id TEXT,details TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS evidence_vault(id BIGSERIAL PRIMARY KEY,transaction_id TEXT REFERENCES transactions(id),category TEXT,severity TEXT,explanation TEXT,source TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE,role TEXT,permissions TEXT,active BOOLEAN DEFAULT TRUE);
        CREATE TABLE IF NOT EXISTS activity_events(id BIGSERIAL PRIMARY KEY,customer_id TEXT REFERENCES customers(id),event_type TEXT,details TEXT,event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,risk_signal DOUBLE PRECISION DEFAULT 0);
        CREATE TABLE IF NOT EXISTS fund_transfers(id BIGSERIAL PRIMARY KEY,source_customer_id TEXT REFERENCES customers(id),target_customer_id TEXT REFERENCES customers(id),amount DOUBLE PRECISION,currency TEXT,beneficiary TEXT,transfer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        ''')
    else:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS customers(id TEXT PRIMARY KEY,name TEXT,avg_amount REAL,max_amount REAL,normal_locations TEXT,normal_merchants TEXT,disputes INTEGER,prior_flags INTEGER,account_age_days INTEGER);
        CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY,customer_id TEXT,amount REAL,currency TEXT,timestamp TEXT,location TEXT,merchant_category TEXT,payment_method TEXT,device_id TEXT,ip_address TEXT,risk_score REAL,status TEXT DEFAULT 'New');
        CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,transaction_id TEXT,status TEXT,assigned_analyst TEXT,analyst_note TEXT,created_at TEXT,updated_at TEXT);
        CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT,action TEXT,entity_id TEXT,details TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS evidence_vault(id INTEGER PRIMARY KEY AUTOINCREMENT,transaction_id TEXT,category TEXT,severity TEXT,explanation TEXT,source TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE,role TEXT,permissions TEXT,active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS activity_events(id INTEGER PRIMARY KEY AUTOINCREMENT,customer_id TEXT,event_type TEXT,details TEXT,event_time TEXT DEFAULT CURRENT_TIMESTAMP,risk_signal REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS fund_transfers(id INTEGER PRIMARY KEY AUTOINCREMENT,source_customer_id TEXT,target_customer_id TEXT,amount REAL,currency TEXT,beneficiary TEXT,transfer_time TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
    default_settings = {
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
    if db.execute('SELECT COUNT(*) AS c FROM settings WHERE key="fraudguard"').fetchone()['c'] == 0:
        db.execute('INSERT INTO settings(key,value) VALUES (?,?)', ('fraudguard', json.dumps(default_settings)))
    if db.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c'] == 0:
        db.executemany('INSERT INTO users(id,email,role,permissions) VALUES (?,?,?,?)', [
            ('analyst', 'analyst@fraudguard.ai', 'Fraud Analyst', json.dumps(['read', 'investigate', 'decide', 'report'])),
            ('admin', 'admin@fraudguard.ai', 'Administrator', json.dumps(['read', 'investigate', 'decide', 'report', 'manage_users', 'manage_settings'])),
        ])
    if db.execute('SELECT COUNT(*) AS c FROM activity_events').fetchone()['c'] == 0:
        db.executemany('INSERT INTO activity_events(customer_id,event_type,details,event_time,risk_signal) VALUES (?,?,?,?,?)', [
            ('C101', 'LOGIN_ANOMALY', 'New device and IP observed from Delhi', (datetime.datetime.now() - datetime.timedelta(minutes=25)).isoformat(timespec='seconds'), 0.8),
            ('C101', 'BENEFICIARY_ADDED', 'New beneficiary added before high-value transfer', (datetime.datetime.now() - datetime.timedelta(minutes=22)).isoformat(timespec='seconds'), 0.9),
            ('C102', 'PASSWORD_RESET', 'Password reset followed by international activity', (datetime.datetime.now() - datetime.timedelta(minutes=18)).isoformat(timespec='seconds'), 0.7),
            ('C104', 'SIM_CHANGE', 'SIM change followed by new device activity', (datetime.datetime.now() - datetime.timedelta(minutes=15)).isoformat(timespec='seconds'), 0.85),
        ])
    if db.execute('SELECT COUNT(*) AS c FROM fund_transfers').fetchone()['c'] == 0:
        db.executemany('INSERT INTO fund_transfers(source_customer_id,target_customer_id,amount,currency,beneficiary,transfer_time) VALUES (?,?,?,?,?,?)', [
            ('C101', 'C102', 85000, 'INR', 'BENEFICIARY-DELTA', (datetime.datetime.now() - datetime.timedelta(minutes=20)).isoformat(timespec='seconds')),
            ('C102', 'C103', 82000, 'INR', 'BENEFICIARY-ECHO', (datetime.datetime.now() - datetime.timedelta(minutes=17)).isoformat(timespec='seconds')),
            ('C103', 'C104', 79000, 'INR', 'BENEFICIARY-FOXTROT', (datetime.datetime.now() - datetime.timedelta(minutes=14)).isoformat(timespec='seconds')),
            ('C104', 'C105', 76000, 'INR', 'BENEFICIARY-GOLF', (datetime.datetime.now() - datetime.timedelta(minutes=11)).isoformat(timespec='seconds')),
            ('C105', 'C101', 74000, 'INR', 'BENEFICIARY-DELTA', (datetime.datetime.now() - datetime.timedelta(minutes=8)).isoformat(timespec='seconds')),
        ])
    if db.execute('SELECT COUNT(*) AS c FROM customers').fetchone()['c'] == 0:
        customers=[
          ('C101','Rahul Sharma',2450,12000,'Bengaluru,Mysuru','Grocery,Food',1,0,900),
          ('C102','Priya Nair',4200,18000,'Kochi,Bengaluru','Travel,Food',0,0,1200),
          ('C103','Arjun Rao',3100,15000,'Hyderabad','Grocery,Utilities',0,1,700),
          ('C104','Sneha Patel',6800,25000,'Mumbai,Pune','Fashion,Food',2,0,1500),
          ('C105','Vikram Singh',5200,22000,'Delhi,Gurugram','Electronics,Food',0,0,500)]
        db.executemany('INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)', customers)
        now=datetime.datetime.now()
        tx=[]
        def add(i,c,a,loc,merchant,minutes,device='DEV-A',ip='10.0.0.1',method='UPI'):
            ts=(now-datetime.timedelta(minutes=minutes)).isoformat(timespec='seconds')
            tx.append((i,c,a,'INR',ts,loc,merchant,method,device,ip,0,'New'))
        add('TXN1001','C101',1200,'Bengaluru','Grocery',60)
        add('TXN1002','C101',2100,'Bengaluru','Food',50)
        add('TXN1003','C101',85000,'Delhi','Electronics',20,'DEV-X','185.44.1.7')
        add('TXN1004','C102',3500,'Kochi','Food',70)
        add('TXN1005','C102',74000,'London','Travel',30,'DEV-Y','91.20.3.4')
        add('TXN1006','C103',1800,'Hyderabad','Utilities',90)
        add('TXN1007','C103',19000,'Hyderabad','Electronics',80)
        add('TXN1008','C104',6200,'Mumbai','Fashion',45)
        add('TXN1009','C104',54000,'Mumbai','Electronics',15,'DEV-Z','172.22.9.1')
        add('TXN1010','C105',500,'Delhi','Food',40)
        add('TXN1011','C105',900,'Delhi','Food',39)
        add('TXN1012','C105',125000,'Chennai','Electronics',35,'DEV-Q','203.1.9.8','Card')
        add('TXN1013','C101',7000,'Bengaluru','Food',5)
        add('TXN1014','C101',7600,'Bengaluru','Food',4)
        add('TXN1015','C101',8100,'Bengaluru','Food',3)
        add('TXN1016','C101',97500,'Dubai','Electronics',2,'DEV-RING-01','185.44.1.7','Card')
        add('TXN1017','C102',118000,'London','Travel',1,'DEV-RING-02','91.20.3.4','Card')
        add('TXN1018','C104',102500,'Chennai','Electronics',3,'DEV-RING-03','203.1.9.8','UPI')
        add('TXN1019','C105',87600,'Mumbai','Electronics',2,'DEV-X','185.44.1.7','Card')
        add('TXN1020','C103',78400,'Dubai','Travel',4,'DEV-Y','91.20.3.4','Card')
        add('TXN1021','C101',6500,'Bengaluru','Food',11)
        add('TXN1022','C104',4300,'Pune','Fashion',12)
        add('TXN1023','C102',11200,'Bengaluru','Food',9)
        db.executemany('INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',tx)
        db.commit()
    from .agents import compute_score_only
    for r in db.execute('SELECT id FROM transactions').fetchall():
        db.execute('UPDATE transactions SET risk_score=? WHERE id=?',(compute_score_only(r['id']),r['id']))
    for r in db.execute('SELECT id,risk_score FROM transactions WHERE risk_score>=75').fetchall():
        cid='CASE-'+r['id'][4:]
        if not db.execute('SELECT 1 FROM cases WHERE id=?',(cid,)).fetchone():
            now=datetime.datetime.now().isoformat(timespec='seconds')
            db.execute('INSERT INTO cases VALUES (?,?,?,?,?,?,?)',(cid,r['id'],'New','analyst','',now,now))
    if db.execute('SELECT COUNT(*) AS c FROM audit_log').fetchone()['c'] == 0:
        db.executemany('INSERT INTO audit_log(action, entity_id, details) VALUES (?, ?, ?)', [
            ('ALERT_GENERATED', 'TXN1003', '{"priority":"high","type":"geo_velocity"}'),
            ('ALERT_GENERATED', 'TXN1016', '{"priority":"critical","type":"card_not_present"}'),
            ('ALERT_GENERATED', 'TXN1017', '{"priority":"critical","type":"travel_anomaly"}'),
            ('ANALYST_DECISION', 'CASE-003', '{"decision":"escalate","note":"High-risk travel pattern and duplicate device footprint."}')
        ])
    db.commit(); db.close()
