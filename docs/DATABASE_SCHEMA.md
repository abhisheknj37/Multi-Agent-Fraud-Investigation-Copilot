# Database Schema

## PostgreSQL core tables

### customers
- id
- name
- avg_amount
- max_amount
- normal_locations
- normal_merchants
- disputes
- prior_flags
- account_age_days

### transactions
- id
- customer_id
- amount
- currency
- timestamp
- location
- merchant_category
- payment_method
- device_id
- ip_address
- risk_score
- status

### cases
- id
- transaction_id
- status
- assigned_analyst
- analyst_note
- created_at
- updated_at

### evidence
- id
- transaction_id
- agent_name
- category
- severity
- explanation
- metric
- created_at

### audit_log
- id
- action
- entity_id
- details
- created_at

## Redis key examples

```text
velocity:{customer_id}:1m
velocity:{customer_id}:5m
risk:{transaction_id}
session:{session_id}
```

## Neo4j labels and relationships

```text
(Customer)
(Account)
(Device)
(IP)
(Merchant)
(Transaction)
(Location)

(Customer)-[:OWNS]->(Account)
(Customer)-[:USES]->(Device)
(Customer)-[:USES]->(IP)
(Customer)-[:MADE]->(Transaction)
(Transaction)-[:AT_MERCHANT]->(Merchant)
(Transaction)-[:AT_LOCATION]->(Location)
```

## OpenSearch indexes

```text
transactions
evidence
audit-logs
investigations
```
