"""Generate additional deterministic synthetic transactions for demos.
Run from project root: python scripts/seed_sample_data.py"""
import csv, random
from pathlib import Path
random.seed(42)
out=Path('data/sample/transactions_500.csv'); out.parent.mkdir(parents=True,exist_ok=True)
customers=[f'C{101+i}' for i in range(20)]
locations=['Bengaluru','Mumbai','Delhi','Hyderabad','Kochi','Chennai','Pune']
merchants=['Food','Grocery','Travel','Electronics','Fashion','Utilities','Gaming']
rows=[]
for i in range(500):
    c=random.choice(customers); fraud=random.random()<0.12
    amount=round(random.uniform(300,12000),2)
    device=f'DEV-{random.randint(1,80):03d}'; ip=f'10.0.{random.randint(0,20)}.{random.randint(1,254)}'
    if fraud:
        amount=round(random.uniform(25000,180000),2); device=random.choice(['DEV-RING-01','DEV-RING-02','DEV-RING-03']); ip=random.choice(['185.44.1.7','91.20.3.4','203.1.9.8'])
    rows.append([f'STXN{i+1:05d}',c,amount,'INR',f'2026-09-{random.randint(1,7):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00',random.choice(locations),random.choice(merchants),'UPI',device,ip,'', 'New', 'fraud' if fraud else 'normal'])
with out.open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','customer_id','amount','currency','timestamp','location','merchant_category','payment_method','device_id','ip_address','risk_score','status','label']); w.writerows(rows)
print(f'Created {out} with {len(rows)} records')
