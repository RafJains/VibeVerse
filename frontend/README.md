# VibeVerse Frontend

Next.js frontend foundation for VibeVerse.

Current scope:

- App Router setup.
- Tailwind CSS styling.
- Entity browsing pages connected to the FastAPI backend.
- Placeholder routes for future feed, communities, collections, profile, and admin phases.

Not included yet:

- Auth
- Reviews
- Collection logic
- Community logic
- Feed logic
- External API ingestion
- Recommendations or ML

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

## Checks

```powershell
npm run typecheck
npm run lint
npm run build
```
