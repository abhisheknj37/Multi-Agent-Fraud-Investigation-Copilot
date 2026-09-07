# Advanced Database Architecture

The upgraded project is designed around a realistic FinTech polyglot persistence model.

## 1. PostgreSQL — System of Record
Use PostgreSQL for authoritative relational data:
- customers
- accounts
- transactions
- merchants
- cases
- fraud alerts
- evidence
- analyst decisions
- audit logs
- agent results

Recommended Python access layer:
- SQLAlchemy 2.x
- asyncpg

## 2. Redis — Real-Time Fraud Signals
Use Redis for:
- transaction velocity counters
- short-lived risk signals
- rate limiting
- session/cache data
- agent state

Example:
`velocity:C101:5m -> 18`

## 3. Neo4j — Fraud Relationship Graph
Use Neo4j for:
- customer ↔ account
- customer ↔ device
- customer ↔ IP
- customer ↔ merchant
- shared infrastructure
- suspicious clusters
- relationship-based investigation

Example Cypher:
```cypher
MATCH (c:Customer)-[:USES]->(d:Device)<-[:USES]-(other:Customer)
WHERE c.id = $customer_id
RETURN other, d
```

## 4. OpenSearch — Investigation Search
OpenSearch is included as an optional advanced search layer for:
- transaction search
- evidence text search
- audit-log search
- IP/device lookup
- high-volume investigation queries

## 5. Why this architecture
Each store has a focused responsibility:
PostgreSQL = correctness and financial records
Redis = speed and real-time counters
Neo4j = relationships
OpenSearch = search

The current demo remains runnable with SQLite for zero-setup demonstration. The advanced infrastructure is provided through Docker Compose and environment configuration so the team can migrate the persistence layer without changing the fraud-agent concepts.

## Buildathon presentation line
"We use polyglot persistence: PostgreSQL as the source of truth, Redis for real-time velocity detection, Neo4j for fraud-network analysis, and OpenSearch for investigator-friendly search."
