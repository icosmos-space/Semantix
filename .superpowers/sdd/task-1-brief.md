### Task 1: Monorepo scaffold (backend + compose)

**Files:**
- Create: `pyproject.toml`, `.env.example`, `.gitignore` (extend if needed)
- Create: `semantix/__init__.py`, `semantix/core/config.py`, `semantix/core/db.py`, `semantix/core/logging.py`, `semantix/core/errors.py`
- Create: `apps/api/main.py`
- Create: `deployments/docker-compose.yml`
- Test: `tests/unit/test_health_import.py`

**Interfaces:**
- Produces: `get_settings() -> Settings`, `get_session()` dependency, `AppError` + exception handlers, `GET /api/v1/health`

- [ ] **Step 1: Write failing import/health test**

```python
# tests/unit/test_health_import.py
from fastapi.testclient import TestClient
from apps.api.main import app

def test_health():
    client = TestClient(app)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

- [ ] **Step 2: Run test — expect fail (module missing)**

```bash
uv run pytest tests/unit/test_health_import.py -v
```

Expected: `ModuleNotFoundError` or collection error.

- [ ] **Step 3: Create `pyproject.toml`**

```toml
[project]
name = "semantix"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.32",
  "sqlalchemy>=2.0",
  "asyncpg>=0.30",
  "alembic>=1.14",
  "pydantic-settings>=2.6",
  "python-jose[cryptography]>=3.3",
  "passlib[bcrypt]>=1.7",
  "httpx>=0.28",
  "sqlglot>=25",
  "cryptography>=43",
]

[dependency-groups]
dev = ["pytest>=8", "pytest-asyncio>=0.24", "ruff>=0.8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["semantix", "apps"]

[tool.pytest.ini_options]
pythonpath = ["."]
asyncio_mode = "auto"
```

- [ ] **Step 4: Implement settings, db stub, errors, health app**

```python
# semantix/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Semantix"
    database_url: str = "postgresql+asyncpg://semantix:semantix@localhost:5432/semantix"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"

def get_settings() -> Settings:
    return Settings()
```

```python
# semantix/core/errors.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "request_id": request.headers.get("X-Request-ID", str(uuid.uuid4())),
                "details": exc.details,
            },
        )
```

```python
# apps/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from semantix.core.config import get_settings
from semantix.core.errors import register_exception_handlers

settings = get_settings()
app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Add compose + `.env.example`**

```yaml
# deployments/docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: semantix
      POSTGRES_PASSWORD: semantix
      POSTGRES_DB: semantix
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://semantix:semantix@localhost:5432/semantix
SECRET_KEY=change-me-in-production
CORS_ORIGINS=http://localhost:5173
```

- [ ] **Step 6: Sync deps and pass health test**

```bash
uv sync
uv run pytest tests/unit/test_health_import.py -v
```

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .env.example apps/ semantix/ tests/unit/test_health_import.py deployments/docker-compose.yml
git commit -m "feat: scaffold FastAPI app with health endpoint"
```

---

