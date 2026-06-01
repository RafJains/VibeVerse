# VibeVerse Backend

FastAPI backend for the VibeVerse structured entertainment intelligence platform.

Current scope:

- Phase 1 backend foundation.
- Phase 2 core entity backend foundation.
- No auth, reviews, collections, communities, feed, ingestion API calls, recommendations, ML, or frontend implementation yet.

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` if your PostgreSQL connection is different from the local default.

## Run Backend

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Health Check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"VibeVerse API"}
```

## Alembic Migrations

Alembic reads `DATABASE_URL` from application settings.

Apply the included initial migration:

```powershell
alembic upgrade head
```

For future model changes, create a new migration:

```powershell
alembic revision --autogenerate -m "create core entity tables"
```

## Seed Data

After PostgreSQL is running and migrations are applied:

```powershell
python -m app.db.seed
```

The seed script inserts sample Film, Series, Song, Album, and Person entities.

## Entity API Examples

List entities:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities"
```

Filter by entity type:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities?entity_type=film"
```

Search by name:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities?search=Inception"
```

Get one entity:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities/1"
```

Create an entity through the temporary unprotected admin route:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/entities" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"name":"Interstellar","entity_type":"film","description":"A space exploration film.","status":"published","tags":["sci-fi"]}'
```

Admin routes are intentionally unprotected for now. Authentication and authorization are later phases.
