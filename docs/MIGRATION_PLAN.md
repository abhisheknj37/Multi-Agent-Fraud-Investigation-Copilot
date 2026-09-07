# Migration Plan: SQLite Demo -> Advanced FinTech Persistence

1. Keep API and agent interfaces unchanged.
2. Create SQLAlchemy models matching `DATABASE_SCHEMA.md`.
3. Replace direct sqlite3 repository functions with async SQLAlchemy repositories.
4. Use Redis sorted sets/counters for velocity windows.
5. Write customer/device/IP/merchant relationships to Neo4j after transaction ingestion.
6. Index transactions, evidence, and audit events in OpenSearch.
7. Add health checks for PostgreSQL, Redis, Neo4j and OpenSearch.
8. Add environment-based secrets and production authentication.
9. Add integration tests for each datastore.
10. Keep the SQLite path as a local fallback for simple demonstrations.
