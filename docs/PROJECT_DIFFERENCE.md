# What is new in AI Financial Crime Sentinel?

Compared with the original copilot, this version adds:

1. PostgreSQL runtime support through `DATABASE_URL` with automatic schema creation.
2. A fraud-ring API that groups customers sharing device/IP fingerprints.
3. Customer risk-profile API for investigation context.
4. Health endpoint exposing database and dataset counts.
5. A deterministic 500-record synthetic data generator.
6. Automated API and scoring tests.
7. Dockerfile for the FastAPI service and a PostgreSQL app compose file.
8. A clearer product identity suitable for a hackathon demo.

The included SQLite fallback remains useful for local demonstrations where Docker/PostgreSQL is unavailable.
