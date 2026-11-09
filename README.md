# AI Financial Crime Sentinel

<escape>🚀 Live Demo: https://financial-crime-sentinel.onrender.com</escape>  
<escape>📘 API Documentation: https://financial-crime-sentinel.onrender.com/docs</escape>

> Demo deployment on Render free tier. Data may reset after service restarts; use synthetic/demo records only.

A hackathon-ready fraud investigation platform inspired by the original Multi-Agent Fraud Investigation Copilot, redesigned with a stronger investigation workflow.

## Highlights
- Multi-agent transaction, customer-history, risk-scoring and network-intelligence analysis
- Fraud-ring detection through shared device/IP fingerprints
- Customer risk profiles
- Human-in-the-loop case decisions and audit trail
- CSV export and PDF investigation reports
- React + Vite frontend and FastAPI backend
- PostgreSQL support with SQLite fallback for zero-setup demos
- Docker Compose for PostgreSQL, Redis, Neo4j and OpenSearch
- Automated tests and a 500-record synthetic sample-data generator

## Run locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000`.

## PostgreSQL
Set `DATABASE_URL` in `.env` to the PostgreSQL connection string and start PostgreSQL with:
```bash
docker compose up -d postgres
```
The application creates its tables automatically at startup.

## Docker Desktop on Windows (SQLite)
The production container uses SQLite and serves the built React frontend and FastAPI API from one origin. SQLite data is stored in the named Docker volume `fraudguard_data`.

Start the application from PowerShell:
```powershell
cd D:\newproj
docker compose -f docker-compose.app.yml up --build
```

Open `http://localhost:8000/` after the container reports healthy. Stop it with:
```powershell
cd D:\newproj
docker compose -f docker-compose.app.yml down
```

Rebuild after code changes with:
```powershell
cd D:\newproj
docker compose -f docker-compose.app.yml down
docker compose -f docker-compose.app.yml up --build
```

The SQLite volume is retained by `down`. To intentionally delete the persisted database and start fresh:
```powershell
cd D:\newproj
docker compose -f docker-compose.app.yml down -v
```

## Deploy to Render
This repository includes `render.yaml` for a single Render Web Service. In Render, choose **New + → Blueprint**, connect the GitHub repository, and deploy the detected `render.yaml`.

The service builds the multi-stage Docker image, serves React and FastAPI from one URL, and uses `/api/health` as its health check. It keeps SQLite as requested. Render's free web-service filesystem is ephemeral, so SQLite data can reset after a redeploy or service restart; use a paid persistent disk or PostgreSQL when durable production data is required.

After deployment, Render provides a URL similar to:
`https://fraudguard.onrender.com`

## Tests
```bash
pip install pytest httpx
pytest -q
```
## 👥 Team Members

| Name                 | Role                            | GitHub                                                 |
| -------------------- | ------------------------------- | ------------------------------------------------------ |
| **Adarsh B H**       | Team Lead / Frontend Developer  | [@AdarshBH23](https://github.com/AdarshBH23)           |
| **Abhishek N J**     | Full-Stack Developer            | [@abhisheknj](https://github.com/abhisheknj)           |
| **Abubakkar Siddiq** | Multi-Tasker Developer          | [@abubakkar734902](https://github.com/abubakkar734902) |
| **Akshata**          | Presenter / Project Coordinator | [@Akshatah3824](https://github.com/Akshatah3824)       |

### 🏆 Hackathon Team

We are a team of four developers who collaboratively designed, developed, tested, and deployed **AI Financial Crime Sentinel** for the hackathon.

### 🤝 Contributions

* **Adarsh B H** — Frontend development, UI/UX, team coordination
* **Abhishek N J** — Full-stack development, backend integration, database
* **Abubakkar Siddiq** — Feature development, testing, integration
* **Akshata** — Project presentation, documentation, coordination

All team members contributed to the development and successful completion of the project.


## Extra sample data
```bash
python scripts/seed_sample_data.py
```
The generator writes `data/sample/transactions_500.csv`; it is intentionally synthetic and safe for demos.
