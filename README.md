# Semantix 

<p align="center">
<img src="https://img.shields.io/badge/STATUS-WIP-red?style=for-the-badge" alt="WIP" />
</p>

<p align="center">
  <strong>Semantic Intelligence Platform</strong>
</p>

<p align="center">
  <strong>Understand Data. Connect Capabilities. Evolve Intelligence.</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#studio">Studio</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MCP-Supported-7B61FF" alt="MCP" />
  <img src="https://img.shields.io/badge/License-Apache--2.0-blue" alt="License" />
</p>

---

## Overview

**Semantix** is an open-source Semantic Intelligence Platform that connects enterprise data, business systems, and AI capabilities through a unified semantic layer.

It enables AI agents and users to understand business concepts, discover data, query metrics, retrieve business information, and perform cross-source analysis through natural language.

Semantix brings together:

- **Semantic Layer** — Define business entities, relationships, metrics, dimensions, and terminology.
- **Data Intelligence** — Combine semantic queries and Text-to-SQL for natural-language data analysis.
- **Functional Tools** — Connect existing business systems through read-only APIs and tools.
- **Knowledge Tools** — Retrieve business documentation, data dictionaries, SQL examples, and business rules.
- **Capability Registry** — Register, discover, govern, and execute capabilities through a unified interface.
- **Agent Orchestration** — Coordinate semantic queries, functional tools, and knowledge retrieval.
- **MCP Ecosystem** — Expose Semantix capabilities through MCP and connect external MCP servers.
- **Semantix Studio** — A unified web console for managing the entire platform.

### The Core Idea

Enterprise AI needs more than database access and a collection of tools.

It needs to understand what business data means, how metrics are defined, how business entities are related, and which capabilities can provide reliable answers.

Semantix provides a unified semantic foundation for this.

```text
                 Natural Language
                        |
                        v
                 Semantix Agent
                        |
                        v
               Capability Discovery
                        |
                        v
                Capability Registry
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      Semantic      Functional     Knowledge
       Data           Tools          Tools
          |             |             |
          v             v             v
      Wren Core     Business APIs    RAG
      Vanna         External MCP     Documents
      SQLGlot       Custom Tools     SQL Examples
          |             |             |
          +-------------+-------------+
                        |
                        v
                 Unified Results
                        |
                        v
                AI Interpretation
```

### Read-Only by Design

Semantix is designed for enterprise data intelligence and information retrieval.

**All capabilities are read-only.**

It can query databases, retrieve business information, analyze metrics, inspect historical records, and search knowledge bases.

It does not provide capabilities to create, modify, delete, restart, trigger, or otherwise change business data or system state.

This principle applies to:

- SQL queries.
- Functional APIs.
- External MCP tools.
- Custom integrations.
- Agent tool execution.

Read-only behavior is verified through capability governance and execution policies, not inferred solely from HTTP methods or tool descriptions.

---

## Features

### 1. Semantic Layer

A unified business semantic layer that defines how enterprise data should be understood.

- Semantic models.
- Business entities.
- Entity relationships.
- Metrics and dimensions.
- Business terminology and synonyms.
- Business rules.
- MDL-based semantic definitions.
- Semantic validation and versioning.
- SQL compilation and preview.

The semantic layer is the authoritative source for business definitions.

AI-generated SQL examples and historical queries can enrich retrieval, but cannot override published metric definitions.

### 2. Data Intelligence

Support multiple query strategies through a unified query interface.

| Capability | Description |
|---|---|
| Semantic Query | Query using business models and metrics |
| Text-to-SQL | Generate SQL from natural language |
| Hybrid Query | Combine semantic models and SQL generation |
| Metric Query | Query standardized business metrics |
| Cross-source Analysis | Combine results from different capabilities |

Initial engine integrations:

- Wren Core — Semantic modeling and SQL compilation.
- Vanna — Text-to-SQL and SQL example retrieval.
- SQLGlot — SQL parsing, validation, and dialect transformation.

Wren Core and Vanna are integrated as independent engines, not treated as the Agent framework.

Cross-database query execution is handled by an appropriate query engine or federation layer. For example, Trino can be evaluated for PostgreSQL and TDengine federation.

### 3. Functional Tools

Connect existing enterprise systems and expose their read-only query capabilities.

Supported integration approaches:

- OpenAPI / Swagger import.
- REST API.
- External MCP tools.
- gRPC.
- Python SDK.
- Custom functions.

Examples:

| Tool | Description |
|---|---|
| `get_device_detail` | Retrieve device information |
| `get_device_alarms` | Query device alarms |
| `get_device_history` | Retrieve historical device data |
| `get_project_info` | Retrieve project information |
| `get_workorder_list` | Query work orders |
| `get_customer_info` | Retrieve customer information |

Functional Tools can return business data just like Semantic Data capabilities.

The distinction is the source and implementation of the capability, not whether it returns data.

### 4. Knowledge Tools

Connect enterprise knowledge to AI queries.

- Business documentation.
- Data dictionaries.
- SQL examples.
- Historical Q&A.
- Business rules.
- Glossaries.
- RAG retrieval.
- Vector search.
- Knowledge indexing and evaluation.

Knowledge retrieval can provide additional context for semantic discovery and query generation.

### 5. Capability Registry

A unified registry for all platform capabilities.

Three capability categories:

| Category | Purpose | Examples |
|---|---|---|
| Semantic Data | Query structured data using business semantics | Metrics, models, SQL |
| Functional | Retrieve information from business systems | REST APIs, MCP tools |
| Knowledge | Retrieve business knowledge | Documents, glossary, SQL examples |

Every capability has a unified definition:

- Identity and description.
- Capability type and source.
- Input and output schemas.
- Semantic metadata.
- Associated business entities.
- Permission policies.
- Read-only governance.
- Version and publication status.

Capability Discovery allows Agents to find relevant tools based on user intent, business entities, descriptions, tags, and permissions.

### 6. Agent Orchestration

Agents coordinate platform capabilities to answer complex questions.

Responsibilities include:

- Intent understanding.
- Semantic context retrieval.
- Capability discovery.
- Query planning.
- Tool selection.
- Tool execution.
- Result aggregation.
- Answer generation.
- Execution trace and audit.

Agents do not access databases or external APIs directly. All execution goes through the Capability Executor and governance layer.

The Agent framework is designed behind an adapter interface to avoid coupling the platform to a single framework.

### 7. MCP Ecosystem

Semantix supports both MCP Server and MCP Client.

**MCP Server**

Expose Semantix capabilities to external AI applications and agents.

Example tools:

- `search_semantic_models`
- `get_model_definition`
- `search_metrics`
- `get_metric_definition`
- `query_metric`
- `query_semantic_model`
- `analyze_data`
- `get_device_alarms`

**MCP Client**

Connect external MCP servers, discover tools, enrich their business semantics, and register approved read-only capabilities.

All MCP tool calls are subject to the same capability governance and execution policies.

---

## Architecture

```text
                       Users / External Agents
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
           Semantix Studio                 MCP Clients
           ChatBI / REST API                   |
                 |                             |
                 +--------------+--------------+
                                |
                         FastAPI Gateway
                                |
                     Authentication / RBAC
                                |
                        Agent Orchestrator
                                |
                       Capability Discovery
                                |
                       Capability Registry
                                |
                     Read-only Capability
                            Executor
                                |
                     Policy / Audit Layer
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
        Semantic Data      Functional Tools    Knowledge Tools
             |                  |                  |
        +----+----+        +----+-----+       +----+----+
        |         |        |          |       |         |
     Wren Core  Vanna   OpenAPI     MCP      RAG    Glossary
        |         |     REST API   Custom   Documents SQL Examples
        +----+----+        |          |       +---------+
             |             |          |
             v             v          v
        Query Engine   Business APIs  External Systems
             |
       SQL Validation
             |
       Query Execution
             |
      PostgreSQL / MySQL /
      TDengine / Other Sources
```

### Core Components

| Component | Responsibility |
|---|---|
| FastAPI Gateway | Unified HTTP API and authentication |
| Semantic Layer | Business models, metrics, relationships, MDL |
| Data Intelligence | Semantic Query and Text-to-SQL |
| Capability Registry | Unified capability management |
| Capability Discovery | Capability retrieval and matching |
| Capability Executor | Controlled capability execution |
| Agent Orchestrator | Intent understanding and task coordination |
| MCP Server | Expose platform capabilities |
| MCP Client | Connect external MCP servers |
| Knowledge Engine | Document and knowledge retrieval |
| Security & Audit | Authorization, execution policies, audit logs |
| Evolution Engine | Discover semantic improvement candidates |

### Design Principles

1. **Semantic-first** — Published business semantics are authoritative.
2. **Capability-driven** — All tools are registered and executed through a unified capability model.
3. **Read-only by design** — The platform provides information retrieval and analysis, not business mutations.
4. **Framework-independent** — Agent frameworks and query engines are replaceable through adapters.
5. **MCP-native** — MCP is both an integration interface and an external capability exposure protocol.
6. **Governance-first** — Authentication, authorization, SQL validation, execution limits, and audit are built into the execution path.

---

## Semantix Studio

Semantix Studio is the visual management console for the entire platform.

It provides a unified interface for configuring data sources, semantic models, business integrations, capabilities, MCP servers, Agents, and ChatBI.

### Studio Modules

| Module | Features |
|---|---|
| Dashboard | Platform overview, statistics, service status |
| Data Sources | Database connections, schema discovery, metadata browsing |
| Semantic Studio | Models, relationships, metrics, glossary, MDL editor |
| Capability Center | Semantic Data, Functional Tools, Knowledge Tools |
| API Integrations | OpenAPI import, REST configuration, authentication |
| MCP Management | MCP Server, MCP Client, tool discovery |
| Agent Studio | Agent configuration, model selection, tool permissions |
| ChatBI | Natural-language data queries and analysis |
| Knowledge Center | Documents, SQL examples, glossary, retrieval testing |
| Semantic Evolution | Candidate metrics, terminology, relationship suggestions |
| Monitoring & Audit | Query logs, execution traces, API and MCP logs |
| System Settings | Users, roles, projects, LLM providers, system configuration |

### Dashboard

Monitor:

- Data source health.
- Published semantic models and metrics.
- Capability count.
- MCP connection status.
- Agent execution statistics.
- Query success rate.
- Average query latency.
- Recent errors and audit events.

### Semantic Studio

Visual and textual semantic model editing.

- Model generation from database schemas.
- Visual entity relationship editor.
- Metric definition editor.
- Business glossary.
- MDL YAML editor.
- SQL compilation preview.
- Validation and version comparison.

### Integration Studio

Import and manage business APIs.

- OpenAPI document import.
- Endpoint and schema browser.
- Authentication configuration.
- Business semantic enrichment.
- Read-only verification.
- Capability publishing.

Raw API specifications and user-maintained semantic definitions are stored separately to prevent API synchronization from overwriting business metadata.

### Capability Center

Manage all capabilities in one place.

- Capability discovery.
- Capability details.
- Input and output schemas.
- Permission configuration.
- Version management.
- Test Playground.
- Execution history.

### Agent Studio

Configure Agents without tightly coupling the platform to a particular framework.

- Agent instructions.
- Model provider and model selection.
- Allowed capabilities.
- Context configuration.
- Execution limits.
- Test conversations.
- Execution traces.

### ChatBI

A conversational interface for enterprise data analysis.

- Natural-language questions.
- Metric queries.
- Text-to-SQL.
- Business API queries.
- Hybrid analysis.
- SQL inspection.
- Tables and charts.
- Query history.
- Follow-up questions.

### Monitoring & Audit

A unified view of platform execution.

- SQL execution logs.
- Functional Tool logs.
- MCP invocation logs.
- Agent execution traces.
- Data source errors.
- Slow queries.
- User activity audit.

---

## Technology Stack

The initial release uses Python for the backend and Vue 3 for the Studio frontend.

### Backend

| Technology | Purpose |
|---|---|
| Python 3.12+ | Main language |
| FastAPI | API framework |
| Pydantic | Data validation and schemas |
| SQLAlchemy 2.0 | ORM and database access |
| Alembic | Database migrations |
| PostgreSQL | Platform metadata storage |
| pgvector | Optional vector storage |
| SQLGlot | SQL parsing and validation |
| FastMCP | MCP Server and Client |
| Pydantic AI | Initial Agent framework candidate |
| APScheduler | Lightweight scheduled jobs |

### Intelligence Engines

| Technology | Purpose |
|---|---|
| Wren Core | Semantic modeling and SQL compilation |
| Vanna | Text-to-SQL and SQL example retrieval |
| Trino | Optional cross-database federation |
| Embedding Models | Semantic retrieval |
| Vector Database | Knowledge retrieval |

### Frontend

| Technology | Purpose |
|---|---|
| Vue 3 | Frontend framework |
| TypeScript | Type safety |
| Vite | Build tool |
| Element Plus | UI components |
| Pinia | State management |
| Vue Router | Routing |
| ECharts | Data visualization |
| Vue Flow | Visual semantic modeling |
| Monaco Editor | MDL and SQL editor |

### Deployment

- Docker
- Docker Compose
- PostgreSQL
- Optional Redis
- Optional Trino

The initial architecture avoids unnecessary infrastructure dependencies. Components such as Redis and Temporal can be introduced when actual workload requirements justify them.

---

## Project Structure

```text
semantix/
├── apps/
│   ├── api/                    # FastAPI application
│   ├── mcp/                    # MCP Server application
│   └── worker/                 # Background jobs
│
├── semantix/
│   ├── core/                   # Configuration, database, logging
│   ├── datasource/             # Data source management
│   ├── semantic/               # Semantic Layer and MDL
│   │   ├── mdl/
│   │   ├── metrics/
│   │   ├── entities/
│   │   ├── relationships/
│   │   └── glossary/
│   │
│   ├── capability/             # Capability Registry and Executor
│   ├── integrations/           # External integrations
│   │   ├── openapi/
│   │   ├── http/
│   │   ├── mcp/
│   │   ├── grpc/
│   │   └── custom/
│   │
│   ├── engines/                # Query engine adapters
│   │   ├── base.py
│   │   ├── wren/
│   │   └── vanna/
│   │
│   ├── query/                  # Query planning and execution
│   ├── knowledge/              # RAG and knowledge retrieval
│   ├── agent/                  # Agent orchestration
│   │   ├── base.py
│   │   ├── context.py
│   │   ├── registry.py
│   │   ├── adapters/
│   │   └── workflows/
│   │
│   ├── mcp/                    # MCP adapters and managers
│   ├── security/               # Authentication and authorization
│   ├── evolution/              # Semantic evolution
│   ├── audit/                  # Audit and execution logs
│   └── models/                 # Shared data models
│
├── web/                        # Semantix Studio
│   └── src/
│       ├── api/
│       ├── components/
│       ├── layouts/
│       ├── router/
│       ├── stores/
│       ├── views/
│       │   ├── dashboard/
│       │   ├── datasources/
│       │   ├── semantic/
│       │   ├── capabilities/
│       │   ├── integrations/
│       │   ├── mcp/
│       │   ├── agents/
│       │   ├── chatbi/
│       │   ├── knowledge/
│       │   ├── evolution/
│       │   ├── monitoring/
│       │   └── settings/
│       └── types/
│
├── mdl/                        # Semantic model definitions
│   ├── schemas/
│   └── examples/
│
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── deployments/
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── docs/
│   ├── architecture.md
│   ├── semantic-model.md
│   ├── capability.md
│   ├── mcp.md
│   └── development.md
│
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Query Workflow

### Semantic Query

```text
User Question
      |
      v
Semantic Context Retrieval
      |
      v
Wren Core Adapter
      |
      v
SQL Compilation
      |
      v
SQLGlot Validation
      |
      v
Read-only Query Execution
      |
      v
Result Formatting
```

### Text-to-SQL

```text
User Question
      |
      v
Schema Context Retrieval
      |
      v
SQL Example Retrieval
      |
      v
Vanna Adapter
      |
      v
SQL Generation
      |
      v
SQLGlot Validation
      |
      v
Read-only Query Execution
      |
      v
Result Formatting
```

### Hybrid Query

A question may require multiple capabilities.

Example:

> Find the five devices with the lowest online rates in the last seven days and retrieve their recent alarms.

```text
User Question
      |
      v
Agent Orchestrator
      |
      v
Capability Discovery
      |
      v
Semantic Data Query
      |
      v
Identify Top 5 Devices
      |
      v
Functional Tool Calls
      |
      v
Retrieve Device Alarms
      |
      v
Result Aggregation
      |
      v
AI Analysis
```

---

## Security and Governance

Security is a fundamental part of Semantix rather than an optional extension.

### SQL Security

- Read-only database credentials.
- Read-only transactions where supported.
- SQL AST validation.
- Single-statement execution.
- Table and column authorization.
- Query timeout.
- Maximum returned rows.
- Restricted system catalogs and sensitive fields.
- Database-level permissions as the final enforcement boundary.

### API Security

- Encrypted credential storage.
- Authentication configuration.
- Request timeout.
- Response size limits.
- API access policies.
- Read-only capability verification.
- Sensitive parameter redaction.

### Capability Governance

- Capability approval and publication.
- User and Agent authorization.
- Source tracking.
- Version management.
- Execution audit.
- External MCP tool review.

### Important

HTTP GET does not automatically guarantee read-only behavior, and HTTP POST does not automatically mean a write operation.

Semantix evaluates the actual semantics and side effects of each integration before allowing it to be published as a read-only capability.

---

## Quick Start

> The following commands describe the planned development environment. They will become executable as the corresponding project components are implemented.

### Requirements

- Python 3.12+
- uv
- Node.js 20+
- PostgreSQL 15+
- Docker and Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/semantix.git
cd semantix
```

### 2. Setup Backend

```bash
uv sync
```

Create your environment configuration:

```bash
cp .env.example .env
```

Configure PostgreSQL and model provider credentials in `.env`.

### 3. Start Infrastructure

```bash
docker compose -f deployments/docker-compose.yml up -d
```

### 4. Run Database Migrations

```bash
uv run alembic upgrade head
```

### 5. Start API

```bash
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Studio

```bash
cd web
npm install
npm run dev
```

### 7. Access Semantix

| Service | Address |
|---|---|
| Studio | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Roadmap

Semantix will be developed incrementally.

| Phase | Features | Status |
|---|---|---|
| Phase 0 | Project foundation, authentication, projects, metadata database | Planned |
| Phase 1 | Data sources, schema discovery, MDL, semantic models | Planned |
| Phase 2 | Wren Core, Vanna, Semantic Query, Text-to-SQL | Planned |
| Phase 3 | Capability Registry, OpenAPI integration, read-only Functional Tools | Planned |
| Phase 4 | MCP Server, MCP Client, external tool discovery | Planned |
| Phase 5 | Agent orchestration, Pydantic AI integration, execution traces | Planned |
| Phase 6 | Knowledge Center, semantic evolution, candidate review | Planned |
| Phase 7 | Complete Studio, monitoring, governance, production deployment | Planned |

### Initial MVP Goals

The first usable version will focus on three scenarios:

**1. Semantic Data Query**

```text
Question:
查询各项目最近 7 天的设备在线率。
```

Use semantic models, published metric definitions, and controlled SQL execution.

**2. Functional Data Query**

```text
Question:
查询设备 tacey_002 最近一天的告警。
```

Use an approved read-only business API.

**3. Hybrid Analysis**

```text
Question:
找出最近 7 天在线率最低的 5 台设备，
并查询它们最近的告警情况。
```

Combine semantic data queries with Functional Tools.

---

## Design Philosophy

Semantix is built around a few simple ideas:

- Business semantics should be defined explicitly, not guessed by AI.
- Metrics should have one authoritative definition.
- Data queries and business information retrieval should share one capability system.
- Agents should discover capabilities instead of hardcoding every integration.
- MCP should connect ecosystems, not dictate internal architecture.
- AI frameworks should remain replaceable.
- All capabilities should be governed through a unified read-only execution boundary.
- Semantic improvements should be reviewed before becoming authoritative.

**Semantix is not another Text-to-SQL wrapper or a generic Agent Builder.**

It aims to become a semantic foundation that enables enterprise data and business information to be understood, queried, and analyzed consistently by AI.

---

## Contributing

Contributions, ideas, bug reports, and architecture discussions are welcome.

Please open an issue before submitting major architectural changes.

---

## License

Semantix is released under the Apache License 2.0.

---

<p align="center">
  <strong>Semantix</strong>
  <br />
  Understand Data. Connect Capabilities. Evolve Intelligence.
</p>
