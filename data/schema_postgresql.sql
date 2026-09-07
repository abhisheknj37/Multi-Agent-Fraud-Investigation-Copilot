CREATE TABLE IF NOT EXISTS customers(id TEXT PRIMARY KEY,name TEXT,avg_amount DOUBLE PRECISION,max_amount DOUBLE PRECISION,normal_locations TEXT,normal_merchants TEXT,disputes INTEGER,prior_flags INTEGER,account_age_days INTEGER);
CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY,customer_id TEXT REFERENCES customers(id),amount DOUBLE PRECISION,currency TEXT,timestamp TEXT,location TEXT,merchant_category TEXT,payment_method TEXT,device_id TEXT,ip_address TEXT,risk_score DOUBLE PRECISION,status TEXT DEFAULT 'New');
CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,transaction_id TEXT REFERENCES transactions(id),status TEXT,assigned_analyst TEXT,analyst_note TEXT,created_at TEXT,updated_at TEXT);
CREATE TABLE IF NOT EXISTS audit_log(id BIGSERIAL PRIMARY KEY,action TEXT,entity_id TEXT,details TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
CREATE TABLE IF NOT EXISTS evidence_vault(id BIGSERIAL PRIMARY KEY,transaction_id TEXT REFERENCES transactions(id),category TEXT,severity TEXT,explanation TEXT,source TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE,role TEXT,permissions TEXT,active BOOLEAN DEFAULT TRUE);
CREATE TABLE IF NOT EXISTS activity_events(id BIGSERIAL PRIMARY KEY,customer_id TEXT REFERENCES customers(id),event_type TEXT,details TEXT,event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,risk_signal DOUBLE PRECISION DEFAULT 0);
CREATE TABLE IF NOT EXISTS fund_transfers(id BIGSERIAL PRIMARY KEY,source_customer_id TEXT REFERENCES customers(id),target_customer_id TEXT REFERENCES customers(id),amount DOUBLE PRECISION,currency TEXT,beneficiary TEXT,transfer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_risk ON transactions(risk_score);
CREATE INDEX IF NOT EXISTS idx_transactions_device_ip ON transactions(device_id,ip_address);

INSERT INTO customers (id,name,avg_amount,max_amount,normal_locations,normal_merchants,disputes,prior_flags,account_age_days)
VALUES
	('C101','Rahul Sharma',2450,12000,'Bengaluru,Mysuru','Grocery,Food',1,0,900),
	('C102','Priya Nair',4200,18000,'Kochi,Bengaluru','Travel,Food',0,0,1200),
	('C103','Arjun Rao',3100,15000,'Hyderabad','Grocery,Utilities',0,1,700),
	('C104','Sneha Patel',6800,25000,'Mumbai,Pune','Fashion,Food',2,0,1500),
	('C105','Vikram Singh',5200,22000,'Delhi,Gurugram','Electronics,Food',0,0,500)
ON CONFLICT (id) DO NOTHING;

INSERT INTO transactions (id,customer_id,amount,currency,timestamp,location,merchant_category,payment_method,device_id,ip_address,risk_score,status)
VALUES
	('TXN1001','C101',1200,'INR','2025-01-15T10:00:00','Bengaluru','Grocery','UPI','DEV-A','10.0.0.1',12,'New'),
	('TXN1002','C101',2100,'INR','2025-01-15T10:10:00','Bengaluru','Food','UPI','DEV-A','10.0.0.1',18,'New'),
	('TXN1003','C101',85000,'INR','2025-01-15T10:40:00','Delhi','Electronics','UPI','DEV-X','185.44.1.7',96,'New'),
	('TXN1004','C102',3500,'INR','2025-01-15T09:50:00','Kochi','Food','UPI','DEV-A','10.0.0.1',10,'New'),
	('TXN1005','C102',74000,'INR','2025-01-15T10:20:00','London','Travel','UPI','DEV-Y','91.20.3.4',91,'New'),
	('TXN1006','C103',1800,'INR','2025-01-15T09:30:00','Hyderabad','Utilities','UPI','DEV-A','10.0.0.1',16,'New'),
	('TXN1007','C103',19000,'INR','2025-01-15T09:40:00','Hyderabad','Electronics','UPI','DEV-A','10.0.0.1',55,'New'),
	('TXN1008','C104',6200,'INR','2025-01-15T10:15:00','Mumbai','Fashion','UPI','DEV-A','10.0.0.1',14,'New'),
	('TXN1009','C104',54000,'INR','2025-01-15T10:45:00','Mumbai','Electronics','UPI','DEV-Z','172.22.9.1',87,'New'),
	('TXN1010','C105',500,'INR','2025-01-15T09:55:00','Delhi','Food','UPI','DEV-A','10.0.0.1',8,'New')
ON CONFLICT (id) DO NOTHING;

INSERT INTO cases (id,transaction_id,status,assigned_analyst,analyst_note,created_at,updated_at)
VALUES
	('CASE-003','TXN1003','New','analyst','','2025-01-15T10:40:00','2025-01-15T10:40:00'),
	('CASE-005','TXN1005','New','analyst','','2025-01-15T10:20:00','2025-01-15T10:20:00'),
	('CASE-009','TXN1009','New','analyst','','2025-01-15T10:45:00','2025-01-15T10:45:00')
ON CONFLICT (id) DO NOTHING;

INSERT INTO settings (key,value)
VALUES ('fraudguard','{"alert_threshold":75,"auto_route_escalations":true,"daily_review_limit":50,"analyst_email":"analyst@fraudguard.ai","notifications_enabled":true}')
ON CONFLICT (key) DO NOTHING;

INSERT INTO users (id,email,role,permissions)
VALUES
	('analyst','analyst@fraudguard.ai','Fraud Analyst','["read","investigate","decide","report"]'),
	('admin','admin@fraudguard.ai','Administrator','["read","investigate","decide","report","manage_users","manage_settings"]')
ON CONFLICT (id) DO NOTHING;

INSERT INTO activity_events (customer_id,event_type,details,event_time,risk_signal)
VALUES
	('C101','LOGIN_ANOMALY','New device and IP observed from Delhi',CURRENT_TIMESTAMP - INTERVAL '25 minutes',0.8),
	('C101','BENEFICIARY_ADDED','New beneficiary added before high-value transfer',CURRENT_TIMESTAMP - INTERVAL '22 minutes',0.9),
	('C102','PASSWORD_RESET','Password reset followed by international activity',CURRENT_TIMESTAMP - INTERVAL '18 minutes',0.7),
	('C104','SIM_CHANGE','SIM change followed by new device activity',CURRENT_TIMESTAMP - INTERVAL '15 minutes',0.85)
ON CONFLICT DO NOTHING;

INSERT INTO fund_transfers (source_customer_id,target_customer_id,amount,currency,beneficiary,transfer_time)
VALUES
	('C101','C102',85000,'INR','BENEFICIARY-DELTA',CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
	('C102','C103',82000,'INR','BENEFICIARY-ECHO',CURRENT_TIMESTAMP - INTERVAL '17 minutes'),
	('C103','C104',79000,'INR','BENEFICIARY-FOXTROT',CURRENT_TIMESTAMP - INTERVAL '14 minutes'),
	('C104','C105',76000,'INR','BENEFICIARY-GOLF',CURRENT_TIMESTAMP - INTERVAL '11 minutes'),
	('C105','C101',74000,'INR','BENEFICIARY-DELTA',CURRENT_TIMESTAMP - INTERVAL '8 minutes');

INSERT INTO audit_log (action,entity_id,details)
VALUES
	('ALERT_GENERATED','TXN1003','{"priority":"high","type":"geo_velocity"}'),
	('ALERT_GENERATED','TXN1005','{"priority":"critical","type":"travel_anomaly"}'),
	('ANALYST_DECISION','CASE-003','{"decision":"escalate","note":"High-risk travel pattern and duplicate device footprint."}');
