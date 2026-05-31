# VibeVerse

VibeVerse is a structured entertainment intelligence and fandom platform. The product direction is IMDb-style entity pages, reviews, collections, organized fandom communities, curated discovery, and recommendation support over time.

This repository currently contains the Phase 1 backend foundation only. Frontend, auth, entities, reviews, communities, feed, ingestion, and recommendation features are intentionally not implemented yet.

## Project Structure

```text
VibeVerse/
├── backend/
├── frontend/
├── ml/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Backend Setup

Create and activate a virtual environment:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a local environment file:

```powershell
copy .env.example .env
```

From the repository root, start PostgreSQL and Redis:

```powershell
cd ..
docker compose up -d
```

Run the FastAPI development server:

```powershell
cd backend
uvicorn app.main:app --reload
```

## Test the API

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"VibeVerse API"}
```

The root endpoint is available at:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"VibeVerse API is running"}
```

## Future Phases

- Phase 2: entity models, schemas, services, admin-safe entity APIs, and seed data.
- Phase 3: reviews, ratings, and collections.
- Phase 4: communities and community-only posts.
- Phase 5: curated global feed.
- Phase 6: backend-only external API ingestion.
- Phase 7: rule-based recommendations.
- Phase 8: AI/ML upgrades.
