from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin_entities import router as admin_entities_router
from app.api.routes.auth import router as auth_router
from app.api.routes.collections import router as collections_router
from app.api.routes.communities import router as communities_router
from app.api.routes.entities import router as entities_router
from app.api.routes.health import router as health_router
from app.api.routes.posts import router as posts_router
from app.api.routes.reviews import router as reviews_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(entities_router)
app.include_router(admin_entities_router)
app.include_router(reviews_router)
app.include_router(collections_router)
app.include_router(communities_router)
app.include_router(posts_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "VibeVerse API is running"}
