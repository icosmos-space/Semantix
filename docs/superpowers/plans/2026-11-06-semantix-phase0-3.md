# Semantix Phase 0–3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a vertical-slice MVP: loginable Studio + datasources/MDL + ChatBI (Markdown + GPT-Vis) + OpenAPI Functional capabilities, covering the three README demo scenarios.

**Architecture:** FastAPI gateway → Capability Registry/Discovery/Read-only Executor → Semantic (Wren/Vanna/SQLGlot) and Functional (OpenAPI) adapters; Vue 3 Studio talks only to `/api/v1`. Phase 3 uses a thin planner; full Agent/MCP land in later phases.

**Tech Stack:** Python 3.12+, uv, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL; Vue 3 + TS + Vite + Element Plus + Pinia; ChatBI via `markdown-it` + `markdown-it-gpt-vis` + `@antv/gpt-vis`; Docker Compose.

**Spec:** `docs/superpowers/specs/2026-11-06-semantix-mvp-design.md`

## Global Constraints

- Read-only by design for SQL, APIs, MCP, and agent tools; no mutation capabilities in MVP.
- Published MDL/metrics are authoritative over AI-generated SQL.
- OpenAPI/MCP imports start as **draft**; publish only after human read-only confirmation.
- Raw OpenAPI spec and ToolSemanticOverlay are stored separately; sync never overwrites overlay.
- Studio never calls Wren/Vanna/business APIs directly.
- ChatBI charts: Markdown fences tagged `GPT-Vis` only; do **not** add ECharts by default.
- `markdown-it-gpt-vis` must be registered **before** any syntax-highlight plugin.
- PG first for datasources; MySQL/TDengine follow without blocking the main path.
- Prefer small focused modules under `semantix/`; adapters isolate Wren/Vanna/Pydantic AI.

---

## Phase 0–7 Roadmap (coarse)

| Phase | Milestone | Done when |
|---|---|---|
| 0 | Foundation | Login + project shell + empty Dashboard via compose |
| 1 | Data + Semantic | Read-only PG → Schema Explorer → save MDL draft |
| 2 | Query intelligence | ChatBI answers with table + audited SQL + GPT-Vis in Markdown |
| 3 | Capability unification | Publish `get_device_alarms`; hybrid Q&A works |
| 4 | MCP | External client calls Semantix tools; inbound draft import |
| 5 | Agent | Configurable Business Analyst + execution traces |
| 6 | Knowledge + Evolution | RAG usable; candidates require human publish |
| 7 | Productization | Prod compose, full RBAC, end-to-end audit |

**Stop fine-grained work after Phase 3.** Phases 4–7 get separate plans later.

---

## File Structure (create / own)

```text
pyproject.toml
.env.example
apps/api/main.py
apps/api/deps.py
semantix/core/{config.py,db.py,logging.py,errors.py}
semantix/models/{base.py,user.py,project.py,datasource.py,semantic.py,capability.py,integration.py,audit.py}
semantix/security/{auth.py,password.py,rbac.py,crypto.py}
semantix/datasource/{service.py,connectors/base.py,connectors/postgres.py,schema_discovery.py}
semantix/semantic/{mdl.py,models_service.py,metrics_service.py,validate.py}
semantix/engines/{base.py,wren/adapter.py,vanna/adapter.py,sqlglot_policy.py}
semantix/query/{service.py,executor.py}
semantix/capability/{registry.py,discovery.py,executor.py,schemas.py}
semantix/integrations/openapi/{import_service.py,overlay.py}
semantix/agent/{planner.py}          # thin Phase 3 planner
semantix/audit/{service.py}
migrations/versions/...
deployments/docker-compose.yml
web/package.json
web/src/{main.ts,App.vue,router/index.ts,stores/{auth.ts,project.ts},api/client.ts}
web/src/layouts/MainLayout.vue
web/src/views/{login,dashboard,datasources,semantic,chatbi,integrations,capabilities}/...
web/src/components/chat/MarkdownMessage.vue
tests/unit/...
tests/integration/...
```

---

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

### Task 2: Metadata DB models + Alembic + auth/projects API

**Files:**
- Create: `semantix/models/base.py`, `user.py`, `project.py`
- Create: `semantix/security/password.py`, `auth.py`, `rbac.py`
- Create: `semantix/core/db.py` (engine + session)
- Create: `migrations/env.py`, `migrations/versions/0001_init_users_projects.py`
- Create: `apps/api/routes/auth.py`, `apps/api/routes/projects.py`, `apps/api/deps.py`
- Modify: `apps/api/main.py` — include routers
- Test: `tests/unit/test_password.py`, `tests/integration/test_auth_flow.py`

**Interfaces:**
- Produces: `User`, `Project`, `Membership`; `create_access_token` / `get_current_user`;  
  `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/projects`, `POST /api/v1/projects`

- [ ] **Step 1: Password unit test**

```python
# tests/unit/test_password.py
from semantix.security.password import hash_password, verify_password

def test_hash_roundtrip():
    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("nope", h)
```

- [ ] **Step 2: Implement password helpers + SQLAlchemy models**

```python
# semantix/security/password.py
from passlib.context import CryptContext
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)
```

```python
# semantix/models/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func
import uuid

class Base(DeclarativeBase):
    pass

def uuid_pk() -> mapped_column:
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

Define `User(id, email, password_hash, display_name, created_at)`, `Project(id, name, slug, created_at)`, `Membership(user_id, project_id, role)` with roles `owner|admin|member|viewer`.

- [ ] **Step 3: Wire async engine + Alembic migration `0001`**

```python
# semantix/core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from semantix.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with SessionLocal() as session:
        yield session
```

Run:

```bash
docker compose -f deployments/docker-compose.yml up -d db
uv run alembic upgrade head
```

- [ ] **Step 4: Auth + projects routes**

JWT via `python-jose`. Login returns `{access_token, token_type}`. Register creates user. Creating a project auto-adds membership `owner`.

- [ ] **Step 5: Integration test with TestClient + overridden DB (or real compose DB)**

```python
def test_register_login_create_project(client):
    r = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "secret123", "display_name": "A"})
    assert r.status_code == 201
    r = client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "secret123"})
    token = r.json()["access_token"]
    r = client.post("/api/v1/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Demo", "slug": "demo"})
    assert r.status_code == 201
```

- [ ] **Step 6: Commit**

```bash
git commit -m "feat: add users, projects, JWT auth, and alembic init"
```

---

### Task 3: Studio shell (login, layout, dashboard placeholder)

**Files:**
- Create: `web/` via `npm create vite@latest web -- --template vue-ts`
- Add deps: `element-plus vue-router pinia axios`
- Create: `web/src/api/client.ts`, `stores/auth.ts`, `stores/project.ts`, `router/index.ts`, `layouts/MainLayout.vue`
- Create: `web/src/views/login/LoginView.vue`, `views/dashboard/DashboardView.vue`
- Modify: `web/vite.config.ts` — proxy `/api` → `http://localhost:8000`

**Interfaces:**
- Consumes: auth/projects APIs from Task 2
- Produces: navigable shell with project switcher; empty Dashboard cards

- [ ] **Step 1: Scaffold Vite app and install UI deps**

```bash
cd web
npm install
npm install element-plus vue-router pinia axios
```

- [ ] **Step 2: API client + auth store**

```ts
// web/src/api/client.ts
import axios from 'axios'
export const api = axios.create({ baseURL: '/api/v1' })
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
```

- [ ] **Step 3: Router guards — redirect unauthenticated users to `/login`**

- [ ] **Step 4: `MainLayout` — left nav stubs (Dashboard, Data Sources, Semantic, ChatBI, Integrations, Capabilities, Settings) + top project switcher**

Nav items for phases not yet built may route to “Coming soon” placeholders; Dashboard + Login must work.

- [ ] **Step 5: Manual accept**

```bash
# terminal 1
uv run uvicorn apps.api.main:app --reload --port 8000
# terminal 2
cd web && npm run dev
```

Open `http://localhost:5173` → register/login → see Dashboard.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(studio): add login shell, layout, and dashboard placeholder"
```

---

### Task 4: Datasources + Schema discovery (PostgreSQL first)

**Files:**
- Create: `semantix/models/datasource.py`
- Create: `semantix/security/crypto.py` (Fernet with `SECRET_KEY`-derived key)
- Create: `semantix/datasource/connectors/base.py`, `postgres.py`, `service.py`, `schema_discovery.py`
- Create: `apps/api/routes/datasources.py`
- Create: migration `0002_datasources.py`
- Create: `web/src/views/datasources/DataSourceListView.vue`, `DataSourceDetailView.vue`, `SchemaExplorer.vue`
- Test: `tests/unit/test_sql_identifier_safety.py`, `tests/integration/test_pg_schema_discovery.py`

**Interfaces:**
- Produces:  
  `DataSourceService.create/test_connection/list/get/sync_schema`  
  `GET/POST /api/v1/projects/{project_id}/datasources`  
  `POST .../datasources/{id}/test`  
  `GET .../datasources/{id}/schema`

- [ ] **Step 1: Failing test for connector interface**

```python
import pytest
from semantix.datasource.connectors.postgres import PostgresConnector

@pytest.mark.asyncio
async def test_postgres_discover_tables(pg_dsn):
    c = PostgresConnector(dsn=pg_dsn)
    schema = await c.discover_schema()
    assert "tables" in schema
```

- [ ] **Step 2: Implement encrypted credential storage + Postgres connector**

Store host/port/db/user/password encrypted at rest. `test_connection` runs `SELECT 1`. Discovery returns databases/schemas/tables/columns/FKs. Enforce read-only intent in UI copy; document that DB user must be read-only.

- [ ] **Step 3: API routes scoped by project membership**

- [ ] **Step 4: Studio list/create/test + Schema Explorer tree**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add datasource management and postgres schema discovery"
```

---

### Task 5: Semantic models + MDL draft/publish

**Files:**
- Create: `semantix/models/semantic.py` (`SemanticModel`, `Metric`, `GlossaryTerm`, `MdlRevision`)
- Create: `semantix/semantic/mdl.py`, `validate.py`, `models_service.py`, `metrics_service.py`
- Create: `apps/api/routes/semantic.py`
- Create: `mdl/schemas/mdl.schema.json` (minimal), `mdl/examples/device_online_rate.yml`
- Create: Studio views under `web/src/views/semantic/` (model list, editor form, Monaco YAML, metrics list)
- Migration `0003_semantic.py`
- Test: `tests/unit/test_mdl_validate.py`

**Interfaces:**
- Produces:  
  `validate_mdl(doc) -> list[ValidationIssue]`  
  CRUD models/metrics; `POST .../mdl/revisions` (draft); `POST .../mdl/revisions/{id}/publish`  
  Example metric: device online rate by project over last 7 days (fixture-friendly)

- [ ] **Step 1: MDL validate failing test**

```python
from semantix.semantic.validate import validate_mdl

def test_rejects_empty_models():
    issues = validate_mdl({"models": []})
    assert any(i.code == "empty_models" for i in issues)
```

- [ ] **Step 2: Minimal MDL YAML shape**

```yaml
# mdl/examples/device_online_rate.yml
models:
  - name: devices
    table: devices
    columns:
      - name: device_id
        type: string
      - name: project_id
        type: string
metrics:
  - name: device_online_rate
    model: devices
    expression: "SUM(CASE WHEN is_online THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0)"
    dimensions: [project_id]
```

- [ ] **Step 3: Services + APIs + Studio editors (form + Monaco)**

Publishing creates immutable revision pointer `published_revision_id` on project/model.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: add semantic models, metrics, and MDL draft/publish"
```

---

### Task 6: SQLGlot read-only policy + query executor

**Files:**
- Create: `semantix/engines/sqlglot_policy.py`
- Create: `semantix/query/executor.py`, `service.py`
- Create: `semantix/models/audit.py` (`QueryRun`)
- Create: `apps/api/routes/query.py` (internal/debug execute endpoint optional)
- Test: `tests/unit/test_sqlglot_policy.py`

**Interfaces:**
- Produces:  
  `assert_readonly_sql(sql: str, dialect: str = "postgres") -> str`  
  `QueryExecutor.execute(datasource_id, sql, actor, *, timeout_s=30, max_rows=1000) -> QueryResult`

- [ ] **Step 1: Write policy tests**

```python
import pytest
from semantix.engines.sqlglot_policy import assert_readonly_sql, SqlPolicyError

def test_allows_select():
    assert assert_readonly_sql("SELECT 1")

def test_rejects_insert():
    with pytest.raises(SqlPolicyError):
        assert_readonly_sql("INSERT INTO t VALUES (1)")

def test_rejects_multi_statement():
    with pytest.raises(SqlPolicyError):
        assert_readonly_sql("SELECT 1; DROP TABLE t")
```

- [ ] **Step 2: Implement AST checks** — only `SELECT`/`WITH`; single statement; block `UPDATE`/`DELETE`/`INSERT`/`MERGE`/`CREATE`/`GRANT`; optional block `pg_catalog` unless allowlisted.

- [ ] **Step 3: Executor uses datasource connector with timeout + `LIMIT` enforcement / truncation + `QueryRun` audit row**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: add SQLGlot read-only policy and audited query executor"
```

---

### Task 7: Wren + Vanna adapters + ChatBI backend

**Files:**
- Create: `semantix/engines/base.py`, `wren/adapter.py`, `vanna/adapter.py`
- Create: `semantix/query/chatbi.py` (orchestrates semantic vs text2sql)
- Create: `semantix/models/chat.py` (`ChatSession`, `ChatMessage`)
- Create: `apps/api/routes/chatbi.py`
- Test: `tests/unit/test_engine_adapters.py`, `tests/integration/test_chatbi_semantic_path.py`

**Interfaces:**
- Produces:  
  `EngineAdapter.compile_or_generate(question, context) -> EngineSql`  
  `POST /api/v1/projects/{id}/chatbi/sessions`  
  `POST /api/v1/projects/{id}/chatbi/sessions/{sid}/messages` →  
  `{ message_id, role, content_markdown, sql, columns, rows, execution_summary }`

**content_markdown contract:** model/service must emit Markdown that may include:

````markdown
以下是近 7 天各项目设备在线率：

```GPT-Vis
vis column
title 近7天设备在线率
data
  - category 项目A
    value 0.92
  - category 项目B
    value 0.81
```

```sql
SELECT ...
```
````

- [ ] **Step 1: Define `EngineAdapter` protocol**

```python
# semantix/engines/base.py
from typing import Protocol
from pydantic import BaseModel

class EngineSql(BaseModel):
    sql: str
    engine: str  # "wren" | "vanna" | "fixture"
    rationale: str | None = None

class EngineAdapter(Protocol):
    async def generate_sql(self, question: str, context: dict) -> EngineSql: ...
```

- [ ] **Step 2: Implement `FixtureEngineAdapter` first (hardcoded mapping for demo question) so acceptance is unblocked**

```python
class FixtureEngineAdapter:
    async def generate_sql(self, question: str, context: dict) -> EngineSql:
        if "在线率" in question:
            return EngineSql(sql="SELECT project_id, online_rate FROM ...", engine="fixture")
        raise NotImplementedError
```

- [ ] **Step 3: Wren/Vanna adapters behind feature flags; fall back to fixture in CI**

- [ ] **Step 4: ChatBI service — retrieve published MDL → prefer Wren/semantic path → on failure optional Vanna if policy allows → SQLGlot → execute → build Markdown answer (table summary + GPT-Vis fence from result columns)**

Helper:

```python
def rows_to_gpt_vis_column(title: str, category_key: str, value_key: str, rows: list[dict]) -> str:
    lines = ["vis column", f"title {title}", "data"]
    for r in rows:
        lines.append(f"  - category {r[category_key]}")
        lines.append(f"    value {r[value_key]}")
    body = "\n".join(lines)
    return f"```GPT-Vis\n{body}\n```"
```

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add ChatBI query path with engine adapters and Markdown answers"
```

---

### Task 8: ChatBI Studio + markdown-it + GPT-Vis

**Files:**
- Create: `web/src/components/chat/MarkdownMessage.vue`, `ChatPanel.vue`, `ExecutionSummary.vue`
- Create: `web/src/views/chatbi/ChatBIView.vue`
- Create: `web/src/utils/markdown.ts`
- Modify: `web/package.json` — add `markdown-it`, `markdown-it-gpt-vis`, `@antv/gpt-vis`, `dompurify`
- Test: `web` manual + optional Vitest for fence detection helper

**Interfaces:**
- Consumes: ChatBI message API
- Produces: three-pane ChatBI (history | conversation | execution summary)

- [ ] **Step 1: Install deps**

```bash
cd web
npm install markdown-it markdown-it-gpt-vis @antv/gpt-vis dompurify
npm install -D @types/markdown-it @types/dompurify
```

- [ ] **Step 2: Markdown pipeline**

```ts
// web/src/utils/markdown.ts
import MarkdownIt from 'markdown-it'
import { gptVisMarkdownItPlugin } from 'markdown-it-gpt-vis'
import DOMPurify from 'dompurify'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })
md.use(gptVisMarkdownItPlugin) // BEFORE any highlight plugin

export function renderChatMarkdown(src: string): string {
  const dirty = md.render(src)
  return DOMPurify.sanitize(dirty, {
    ADD_TAGS: ['gpt-vis'],
    ADD_ATTR: ['data-gpt-vis', 'style', 'class'],
  })
}
```

- [ ] **Step 3: `MarkdownMessage.vue`**

```vue
<template>
  <div class="md-body" v-html="html"></div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { renderChatMarkdown } from '@/utils/markdown'
const props = defineProps<{ content: string }>()
const html = computed(() => renderChatMarkdown(props.content))
</script>
```

Ensure `markdown-it-gpt-vis` registers the Web Component (or call `registerGPTVisElement()` once in `main.ts`).

- [ ] **Step 4: ChatBI view — send question「查询各项目最近 7 天的设备在线率。」→ show MarkdownMessage + SQL in ExecutionSummary + QueryRun id**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(studio): ChatBI with markdown-it and GPT-Vis rendering"
```

---

### Task 9: Capability registry + executor skeleton

**Files:**
- Create: `semantix/models/capability.py`
- Create: `semantix/capability/schemas.py`, `registry.py`, `discovery.py`, `executor.py`
- Create: `apps/api/routes/capabilities.py`
- Migration `0004_capabilities.py`
- Test: `tests/unit/test_capability_state_machine.py`

**Interfaces:**
- Produces:  
  `Capability(kind: semantic_data|functional|knowledge, status: draft|published|disabled, operation: read, ...)`  
  `CapabilityRegistry.register/publish/get/list`  
  `CapabilityDiscovery.search(query, project_id, actor)`  
  `CapabilityExecutor.execute(capability_id, input, actor) -> CapabilityResult`  
  Hard-deny if not `published` or `operation != read`

- [ ] **Step 1: State machine test**

```python
import pytest
from semantix.capability.registry import CapabilityRegistry
from semantix.core.errors import AppError

def test_cannot_execute_draft(registry, draft_cap):
    with pytest.raises(AppError) as e:
        # sync wrapper or asyncio.run in real test
        pass
    assert e.value.code == "capability_not_published"
```

- [ ] **Step 2: Implement registry/executor; semantic query path registers a `semantic.query` capability on publish of MDL (or system capability)**

- [ ] **Step 3: Studio Capability Center list/detail (read-only view) + status badge**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: add capability registry, discovery, and read-only executor"
```

---

### Task 10: OpenAPI import + semantic overlay + Functional tools

**Files:**
- Create: `semantix/models/integration.py` (`Integration`, `RawOpenApiSpec`, `ToolSemanticOverlay`)
- Create: `semantix/integrations/openapi/import_service.py`, `overlay.py`, `http_adapter.py`
- Create: `apps/api/routes/integrations.py`
- Create: Studio `views/integrations/*`, Tool semantic editor, Playground
- Migration `0005_integrations.py`
- Test: `tests/unit/test_overlay_merge.py`, `tests/integration/test_openapi_import_draft.py`

**Interfaces:**
- Produces:  
  Import OpenAPI → draft Functional capabilities  
  `merge_overlay(raw_operation, overlay) -> EffectiveTool`  
  Sync updates Raw spec only  
  Publish after `read_only_confirmed=true`  
  Example tool `get_device_alarms` → GET `/api/device/{device_id}/alarms`

- [ ] **Step 1: Overlay merge test**

```python
from semantix.integrations.openapi.overlay import merge_overlay

def test_sync_does_not_clobber_overlay_description():
    raw = {"operation_id": "getAlarms", "method": "get", "path": "/api/device/{device_id}/alarms"}
    overlay = {"name": "get_device_alarms", "description": "查询设备告警", "intents": ["查询设备告警"]}
    effective = merge_overlay(raw, overlay)
    assert effective["name"] == "get_device_alarms"
    raw2 = {**raw, "summary": "new upstream summary"}
    effective2 = merge_overlay(raw2, overlay)
    assert effective2["description"] == "查询设备告警"
```

- [ ] **Step 2: Import service + host allowlist + draft capabilities**

- [ ] **Step 3: HTTP adapter in Executor for `kind=functional` — timeout, size limit, SSRF allowlist**

- [ ] **Step 4: Studio flows — create integration, import, edit overlay, confirm read-only, publish, Playground invoke**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: OpenAPI import with semantic overlay and functional tools"
```

---

### Task 11: Thin hybrid planner + MVP acceptance demos

**Files:**
- Create: `semantix/agent/planner.py`
- Modify: `semantix/query/chatbi.py` — call planner for multi-capability questions
- Create: `docs/demo/mvp-scenarios.md`
- Create: seed script `scripts/seed_mvp_demo.py` (optional sample schema + mock alarms HTTP)
- Test: `tests/integration/test_hybrid_alarms_flow.py`

**Interfaces:**
- Produces: `Planner.plan(question) -> list[PlanStep]` where steps reference capability ids  
- Hybrid example: semantic top-5 low online-rate devices → map ids → `get_device_alarms`

- [ ] **Step 1: Planner returns ordered steps for hybrid keyword/heuristic (LLM optional behind flag)**

```python
class PlanStep(BaseModel):
    capability_id: str
    input_template: dict
    depends_on: list[int] = []

class Planner:
    async def plan(self, question: str, discovered: list) -> list[PlanStep]:
        ...
```

- [ ] **Step 2: ChatBI aggregates step results into one Markdown answer (with GPT-Vis if useful)**

- [ ] **Step 3: Write `docs/demo/mvp-scenarios.md` with exact prompts:**

1. `查询各项目最近 7 天的设备在线率。`  
2. `查询设备 tacey_002 最近一天的告警。`  
3. `找出最近 7 天在线率最低的 5 台设备，并查询它们最近的告警情况。`

- [ ] **Step 4: Run acceptance checklist manually; fix gaps**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: add hybrid planner and MVP demo scenarios"
```

---

### Task 12: Phase 0–3 hardening pass

**Files:**
- Modify: README Quick Start commands until they work
- Create: `tests/e2e/test_smoke_login_chatbi.py` (optional Playwright later; HTTP smoke OK for MVP)
- Create: `docs/superpowers/plans/phase4-7-stubs.md` pointers only (or section below)

- [ ] **Step 1: Ensure `uv sync`, compose, migrate, API, web documented in README match reality**

- [ ] **Step 2: Add CI-friendly unit suite green**

```bash
uv run pytest tests/unit -v
```

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: harden MVP quick start and unit test suite"
```

---

## Phases 4–7 (stubs only — separate plans later)

### Phase 4 — MCP
- `apps/mcp` FastMCP server exposing published capabilities
- MCP Client connection + draft import + Studio MCP pages
- Acceptance: external MCP client lists/calls `query_metric` / `get_device_alarms`

### Phase 5 — Agent Studio
- Pydantic AI adapter behind `semantix/agent/adapters/`
- Agent config, tool allowlists, step/timeout limits, traces UI
- Acceptance: Business Analyst template hybrid run with visible trace

### Phase 6 — Knowledge + Evolution
- Document ingest, embeddings, SQL examples
- Candidate metrics/terms from query logs; human publish only
- Acceptance: retrieval helps ChatBI; published metrics unchanged without approval

### Phase 7 — Productization
- Full RBAC matrix, secrets UX, monitoring pages, prod compose/images
- Acceptance: deploy checklist + audit completeness

---

## Self-Review

1. **Spec coverage:** Phase 0–3 tasks map to architecture, datasources, MDL, Wren/Vanna/fixture, SQLGlot, ChatBI Markdown+GPT-Vis, Capability, OpenAPI overlay, hybrid planner, three demo scenarios. Phase 4–7 stubbed.  
2. **Placeholders:** None intentionally left as TBD; Wren/Vanna may use fixture fallback but interface is defined.  
3. **Type consistency:** `CapabilityExecutor.execute`, `EngineAdapter.generate_sql`, `merge_overlay`, ChatBI `content_markdown` used consistently.  
4. **GPT-Vis:** Fence language `GPT-Vis`; plugin order documented; DOMPurify whitelist included.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-11-06-semantix-phase0-3.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute in this session with executing-plans checkpoints  

Which approach?
