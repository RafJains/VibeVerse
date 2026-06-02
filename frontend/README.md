# VibeVerse Frontend

Next.js frontend foundation for VibeVerse.

Current scope:

- App Router setup.
- Tailwind CSS styling.
- Entity browsing pages connected to the FastAPI backend.
- Frontend signup, login, logout, and current-user session state.
- Review and save actions use the logged-in user.
- Community browsing, detail, creation, join, leave, and entity-linked community sections.
- Placeholder routes for future feed, full collections, and admin phases.

Not included yet:

- Community posts, comments, polls, or moderation dashboards
- Feed logic
- External API ingestion
- Recommendations or ML
- OAuth, refresh tokens, email verification, or password reset UI

## Setup

```powershell
cd frontend
npm install
copy .env.example .env.local
```

The default API URL is:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Run Backend and Frontend Together

Terminal 1:

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

Entity browsing uses:

```text
GET /entities
GET /entities/{id}
GET /entities/{id}/media
GET /entities/{id}/credits
GET /entities/{id}/related
```

Auth uses:

```text
POST /auth/signup
POST /auth/login
GET /auth/me
POST /auth/logout
```

The frontend stores the JWT access token in `localStorage` for now and sends it
as a Bearer token through the centralized API client.

Review and save actions require a logged-in user. The frontend does not send
`user_id` for those actions; the backend derives ownership from the Bearer token.

Communities use:

```text
GET /communities
GET /communities/{id}
GET /entities/{entity_id}/communities
GET /communities/{id}/members
POST /communities
POST /communities/{id}/join
POST /communities/{id}/leave
```

Creating or joining communities requires a logged-in user. Public browse and
detail pages still work without a session.

## Checks

```powershell
npm run typecheck
npm run lint
npm run build
```
