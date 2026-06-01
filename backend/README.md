# VibeVerse Backend

FastAPI backend for the VibeVerse structured entertainment intelligence platform.

Current scope:

- Phase 1 backend foundation.
- Phase 2 core entity backend foundation.
- Phase 4A backend reviews and ratings foundation.
- No auth, collections, communities, feed, ingestion API calls, recommendations, ML, or frontend review UI yet.

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

The review system is included in migration `0002_create_review_tables.py`. Apply it with the same command:

```powershell
alembic upgrade head
```

## Seed Data

After PostgreSQL is running and migrations are applied:

```powershell
python -m app.db.seed
```

The seed script inserts sample Film, Series, Song, Album, and Person entities.
It also inserts demo users and sample reviews when review tables are migrated.

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

## Review API Examples

Auth is not implemented yet, so review write requests accept `user_id` directly.

List reviews for an entity:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities/1/reviews"
```

Alternative entity reviews route:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews/entity/1"
```

Get a rating summary:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities/1/rating-summary"
```

Create a review:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"entity_id":1,"user_id":1,"rating":4.5,"title":"Strong watch","body":"A polished entertainment experience.","spoiler":false,"visibility":"public","tags":["sample"]}'
```

Update a review:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews/1" `
  -Method Patch `
  -ContentType "application/json" `
  -Body '{"rating":5.0,"body":"Updated review body.","tags":["updated"]}'
```

Report a review:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews/1/report" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"reporter_user_id":2,"reason":"spoiler","details":"This review may need a spoiler flag."}'
```
