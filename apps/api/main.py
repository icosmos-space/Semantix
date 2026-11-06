from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes import auth, chatbi, datasources, projects, query, semantic
from semantix.core.config import get_settings
from semantix.core.errors import register_exception_handlers

settings = get_settings()
app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(datasources.router, prefix="/api/v1")
app.include_router(semantic.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(chatbi.router, prefix="/api/v1")





@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
