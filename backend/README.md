# VibeVerse Backend

FastAPI backend for the VibeVerse structured entertainment intelligence platform.

Current scope:

- Phase 1 backend foundation.
- Phase 2 core entity backend foundation.
- Phase 4A backend reviews and ratings foundation.
- Phase 4B backend collections foundation.
- Phase 5A backend auth foundation.
- Phase 5C auth-protected user write actions.
- Phase 6A backend communities core.
- Phase 6C backend community posts core.
- Phase 7A curated global feed backend foundation.
- Phase 8A backend external API ingestion foundation.
- No frontend ingestion UI, recommendations, or ML yet.

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
TMDb and YouTube API keys are optional for local setup, but admin ingestion endpoints return a clear missing-key error when a required key is absent.

External API keys:

```env
TMDB_API_KEY=
TMDB_BASE_URL=https://api.themoviedb.org/3
YOUTUBE_API_KEY=
YOUTUBE_BASE_URL=https://www.googleapis.com/youtube/v3
```

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

The community core is included in migration `0005_create_community_tables.py`. Apply it with:

```powershell
alembic upgrade head
```

The community posts core is included in migration `0006_create_community_post_tables.py`. Apply it with:

```powershell
alembic upgrade head
```

The curated global feed core is included in migration `0007_create_feed_tables.py`. Apply it with:

```powershell
alembic upgrade head
```

Phase 8A ingestion uses existing tables from the core entity migration:

- `external_ids`
- `raw_external_payloads`
- `ingestion_jobs`
- `entity_media`
- `entity_tags`

No Alembic migration is required for Phase 8A.

## Seed Data

After PostgreSQL is running and migrations are applied:

```powershell
python -m app.db.seed
```

The seed script inserts sample Film, Series, Song, Album, and Person entities.
It also inserts demo users and sample reviews when review tables are migrated.
It also inserts sample watchlist, favourites, and custom collections when collection tables are migrated.
It also inserts sample communities when community tables are migrated.
It also inserts sample community posts when community post tables are migrated.
It also inserts an admin user, sample curated global feed cards, and manual trending scores when feed tables are migrated.

Seeded auth credentials:

- `demo_user` / `demo12345`
- `critic_user` / `critic12345`
- `admin_user` / `admin12345`

Sample seeded communities:

- `Inception Fans`
- `Demon Slayer Corps`
- `Weeknd Listeners`

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
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"entity_id":1,"rating":4.5,"title":"Strong watch","body":"A polished entertainment experience.","spoiler":false,"visibility":"public","tags":["sample"]}'
```

Update a review:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews/1" `
  -Method Patch `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"rating":5.0,"body":"Updated review body.","tags":["updated"]}'
```

Report a review:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/reviews/1/report" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"reason":"spoiler","details":"This review may need a spoiler flag."}'
```

Review write routes require a Bearer token. The server derives `user_id` and
`reporter_user_id` from the authenticated user instead of trusting request body IDs.

## Collection API Examples

List collections for a user:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/collections/user/1"
```

The `/collections/user/{user_id}` route is temporary dev compatibility. Prefer:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/me/collections" `
  -Headers @{ Authorization = "Bearer $token" }
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
Invoke-RestMethod "http://127.0.0.1:8000/me/watchlist/1" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" }
```

Save to favourites:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/me/favourites/3" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" }
```

Temporary dev compatibility routes still exist while the frontend migrates fully:

- `POST /users/{user_id}/watchlist/{entity_id}`
- `DELETE /users/{user_id}/watchlist/{entity_id}`
- `POST /users/{user_id}/favourites/{entity_id}`
- `DELETE /users/{user_id}/favourites/{entity_id}`

## Community API Examples

Community posts exist only inside communities. They are not global feed posts.
The global feed remains curated/admin-controlled and is not part of this phase.

List communities:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities"
```

List communities linked to an entity:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/entities/1/communities"
```

Get a community by id:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1"
```

Get a community by slug:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/slug/inception-fans"
```

Create a fan community:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"name":"Synth Pop Fans","description":"Discussion for synth-pop releases.","community_type":"fan","entity_id":4}'
```

Join a community:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/join" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" }
```

Add a community rule as owner, moderator, or admin:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/rules" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"title":"Keep discussion on-topic","description":"Posts should relate to the linked entertainment entity.","order_index":1}'
```

Report a community:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/report" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"reason":"duplicate","details":"This may duplicate another community."}'
```

## Community Post API Examples

List posts for a community:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/posts"
```

Create a post inside a community:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/posts" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"post_type":"discussion","title":"First theory thread","body":"This only appears inside the community.","spoiler":false}'
```

Update your own post:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/posts/1" `
  -Method Patch `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"title":"Updated theory thread","body":"Updated community-only post body."}'
```

Report a post:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/posts/1/report" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"reason":"spoiler","details":"This may need a spoiler flag."}'
```

Hide a post as a community owner, moderator, admin, or super admin:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/posts/1/hide" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"reason":"Needs moderation review."}'
```

Add a blocked word as a community owner, moderator, admin, or super admin:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/communities/1/blocked-words" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"word":"blockedterm"}'
```

## Curated Global Feed API Examples

Global feed is curated/admin-controlled. Community posts do not appear here.

List public global feed cards:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/feed/global"
```

Filter public global feed cards by region:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/feed/global?region=global"
```

Get a public feed card:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/feed/cards/1"
```

List trending scores:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/feed/trending-scores"
```

Login as the seeded admin:

```powershell
$adminLogin = Invoke-RestMethod "http://127.0.0.1:8000/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email_or_username":"admin_user","password":"admin12345"}'

$adminToken = $adminLogin.access_token
```

Create an admin feed card:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/feed-cards" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"title":"Curated spotlight","subtitle":"Admin controlled card","body":"This is not a community post.","card_type":"spotlight","linked_entity_ids":[1],"priority":10,"region":"global"}'
```

Approve and publish a feed card:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/feed-cards/1/approve" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" }

Invoke-RestMethod "http://127.0.0.1:8000/admin/feed-cards/1/publish" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" }
```

Link an entity to a feed card:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/feed-cards/1/entities/2?order_index=1" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" }
```

## External API Ingestion Examples

External APIs must be called only from backend ingestion services. The frontend must not call TMDb or YouTube directly.

Login as admin:

```powershell
$adminLogin = Invoke-RestMethod "http://127.0.0.1:8000/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"email_or_username":"admin_user","password":"admin12345"}'

$adminToken = $adminLogin.access_token
```

List ingestion jobs:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/jobs" `
  -Headers @{ Authorization = "Bearer $adminToken" }
```

Search TMDb and store the raw search payload:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/tmdb/search" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"query":"Inception"}'
```

Ingest a TMDb movie into a VibeVerse Film entity:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/tmdb" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"tmdb_id":27205,"tmdb_type":"movie","import_media":false}'
```

Ingest a TMDb TV series:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/tmdb" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"tmdb_id":1399,"tmdb_type":"tv","import_media":false}'
```

Ingest a TMDb person:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/tmdb" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"tmdb_id":525,"tmdb_type":"person","import_media":false}'
```

Ingest YouTube media for an existing entity:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/ingestion/youtube" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $adminToken" } `
  -ContentType "application/json" `
  -Body '{"entity_id":1,"max_results":5}'
```

If `TMDB_API_KEY` or `YOUTUBE_API_KEY` is missing, the corresponding ingestion endpoint returns a clear `503` response instead of making an external request.
