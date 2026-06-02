# VibeVerse Backend

FastAPI backend for the VibeVerse structured entertainment intelligence platform.

Current scope:

- Phase 1 backend foundation.
- Phase 2 core entity backend foundation.
- Phase 4A backend reviews and ratings foundation.
- Phase 4B backend collections foundation.
- Phase 5A backend auth foundation.
- No frontend auth UI, communities, feed, ingestion API calls, recommendations, or ML yet.

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` if your PostgreSQL connection is different from the local default.
Set a strong `SECRET_KEY` before production deployment. The example value is for local development only.

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

The collection system is included in migration `0003_create_collection_tables.py`. Apply it with:

```powershell
alembic upgrade head
```

The auth user fields are included in migration `0004_add_auth_fields_to_users.py`. Apply it with the same command:

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
It also inserts sample watchlist, favourites, and custom collections when collection tables are migrated.

Seeded auth credentials:

- `demo_user` / `demo12345`
- `critic_user` / `critic12345`

## Auth API Examples

Create a user:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/auth/signup" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email":"newuser@vibeverse.dev","username":"new_user","password":"newuser123"}'
```

Login with username or email:

```powershell
$login = Invoke-RestMethod "http://127.0.0.1:8000/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email_or_username":"demo_user","password":"demo12345"}'

$token = $login.access_token
```

Get the current user:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/auth/me" `
  -Headers @{ Authorization = "Bearer $token" }
```

Logout placeholder:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/auth/logout" -Method Post
```

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

Frontend auth UI is not implemented yet, so review write requests still accept `user_id` directly.

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

## Collection API Examples

Frontend auth UI is not implemented yet, so collection requests still accept `user_id` directly.

List collections for a user:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/user/1"
```

Get a collection:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/1"
```

List collection items:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/1/items"
```

Create a custom collection:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"user_id":1,"name":"Comfort picks","description":"Entities to revisit.","collection_type":"custom_collection","visibility":"private"}'
```

Add an entity to a collection:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/1/items" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"entity_id":4,"note":"Add this next.","order_index":3}'
```

Remove an entity from a collection:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/1/items/4" -Method Delete
```

Save to watchlist:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/users/1/watchlist/1" -Method Post
```

Save to favourites:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/users/1/favourites/3" -Method Post
```
