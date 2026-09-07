# Architecture

## Agents
1. Transaction-Pattern Agent
   - Amount anomaly
   - Velocity
   - Geography
   - Merchant category
   - Time anomaly
   - Device/IP anomaly
   - Duplicate transaction check

2. Customer-History Agent
   - Spending baseline
   - Historical maximum
   - Normal locations
   - Normal merchants
   - Disputes
   - Prior flags
   - Account age

3. Risk-Scoring Agent
   - Aggregates weighted evidence
   - Produces risk level and confidence
   - Produces recommendation

## Human-in-the-loop
The AI does not make the final decision. The analyst chooses:
- Clear
- Confirm Fraud
- Escalate

## Production upgrade path
- Replace SQLite with PostgreSQL
- Add JWT/OAuth authentication
- Add a real fraud ML model
- Add geolocation/device intelligence providers
- Add vector database + embeddings for RAG
- Add an LLM with structured JSON output
- Add queue/event streaming
- Add secrets management and encryption
