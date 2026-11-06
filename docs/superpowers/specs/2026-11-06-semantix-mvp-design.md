# Semantix Design Spec

**Date:** 2026-11-06  
**Status:** Draft for review  
**Sources:** ChatGPT shares（命名ChatBI 1/2）、仓库 README、本轮拍板结论  

## 1. Goal

构建开源 **Semantic Intelligence Platform（Semantix）**：以统一语义层为核心，融合自然语言数据查询、只读业务能力接入、MCP、以及后续指标知识进化；配套完整 **Semantix Studio**。

一句话定位：

> 一个以统一语义层为核心，融合自然语言数据查询、MCP 能力集成与指标知识进化的开源 AI 数据智能平台。

## 2. Non-Goals（YAGNI）

- 业务写操作（创建/修改/删除/重启等）及写操作审批流
- 把 Agent 做成复杂可视化工作流编排器（先配置式 Agent）
- Phase 0–3 内完整 Knowledge / Semantic Evolution / 深度 MCP Client
- 默认引入 Redis、Temporal、Trino（有明确负载再加）
- 默认引入 ECharts（ChatBI/Dashboard 优先 GPT-Vis）

## 3. Product Boundaries

- **只读 by design**：SQL、Functional API、外部 MCP、自定义集成、Agent 工具执行一律只读。
- 只读性靠治理与人工审核确认，不单凭 HTTP 方法或工具描述推断。
- 已发布语义（MDL/指标）为权威；AI 生成 SQL/候选不能覆盖已发布定义。
- Agent 与查询引擎通过 Adapter 接入，可替换。
- Studio 前端只调用 Semantix FastAPI，不直连 Wren / Vanna / 业务系统。

## 4. Delivery Approach

采用 **纵向切片（方案 1）**：每个 Phase 交付「后端能力 + Studio 页面 + 可演示场景」。

计划粒度：

- **全路线图**：Phase 0–7（里程碑 + 验收）
- **细实现计划**：Phase 0–3（可执行任务级，另见 plans 文档）

MVP 截止线：Phase 3 结束，跑通 README 三场景：

1. 语义/指标自然语言查询  
2. Functional 只读业务查询  
3. 混合分析（如最低在线率设备 + 告警）

## 5. Architecture

```text
Studio / ChatBI / External Agents (MCP)
              ↓
        FastAPI Gateway + Auth/RBAC
              ↓
        Agent Orchestrator
        （Phase 3 简化 Planner；Phase 5 厚做）
              ↓
   Capability Discovery ← Capability Registry
              ↓
        Read-only Executor + Policy/Audit
        ┌─────────┼─────────┐
   Semantic Data  Functional  Knowledge
   Wren / Vanna   OpenAPI     （Phase 6）
   SQLGlot
```

### 5.1 Capability kinds

| Kind | Role | MVP |
|---|---|---|
| Semantic Data | MDL/指标查询、Text-to-SQL | Phase 1–2 |
| Functional | 业务系统只读 API | Phase 3 |
| Knowledge | 文档/术语/SQL 示例 | Phase 6 |

统一执行入口：

`CapabilityExecutor.execute(capability_id, input, actor)` → Policy → 执行 → Audit。

### 5.2 Core components

| Component | Responsibility |
|---|---|
| FastAPI Gateway | HTTP API、认证 |
| Semantic Layer | MDL、实体、关系、指标、术语、版本 |
| Data Intelligence | Wren / Vanna / SQLGlot 适配与查询 |
| Capability Registry / Discovery / Executor | 能力注册、检索、只读执行 |
| Integrations | OpenAPI 导入；源 Spec 与语义 Overlay 分离 |
| Agent Orchestrator | 意图、规划、工具选择、聚合解释 |
| MCP Server/Client | 对外暴露 / 接入外部工具（Phase 4） |
| Knowledge / Evolution | RAG 与候选审核（Phase 6） |
| Security & Audit | RBAC、策略、审计 |
| Semantix Studio | 管理与 ChatBI 控制台 |

## 6. Phase Roadmap & Acceptance

| Phase | Goal | Backend | Studio | Acceptance |
|---|---|---|---|---|
| **0** 地基 | 可登录空壳 | uv + FastAPI、PG 元库、Alembic、用户/项目/RBAC 骨架、健康检查 | 登录、项目切换、导航壳、Dashboard 占位 | compose → 登录 → 见项目与空 Dashboard |
| **1** 数据与语义 | 管库建模 | 数据源 CRUD、连接测试、Schema 发现（PG 优先，MySQL/TDengine 跟进）、MDL 存取/校验/草稿版本 | 数据源、Schema Explorer、模型编辑（表单 + YAML） | 只读 PG → Schema → 保存语义模型 |
| **2** 查询智能 | NL 查数 | Wren、Vanna、SQLGlot、只读执行（超时/行数）、查询审计；ChatBI 回答含 Markdown+GPT-Vis | 指标基础、ChatBI（会话/表/SQL/图） | 「各项目近 7 天设备在线率」→ 表 + 可审计 SQL + MD 内图表 |
| **3** 能力统一 | API 进同一套 | OpenAPI 导入、只读审核、Registry/Discovery/Executor、Overlay 与 Raw Spec 分离、简化混合编排 | Integrations、Tool 语义编辑、Capability Center、Playground | 发布 `get_device_alarms`；混合问法可跑通 |
| **4** MCP | 能力双向 | FastMCP Server；MCP Client 发现+草稿 | MCP 管理与日志 | 外部可调 Semantix；外部工具可审核注册 |
| **5** Agent | 可配置编排 | Pydantic AI Adapter、权限/步数/超时、轨迹 | Agent Studio、测试对话、轨迹 | Business Analyst 模板：语义 + Functional 联合 |
| **6** 知识与进化 | 知识+候选 | RAG/术语/示例；候选流水线（不自动改权威定义） | Knowledge、Evolution 审核 | 检索可用；候选须人工发布 |
| **7** 产品化 | 可部署治理 | 完整 RBAC、密钥、监控、生产 compose | 监控审计、系统设置 | 一键部署；审计可追人/能力/SQL/API |

## 7. MVP Tech Stack (Phase 0–3)

### Backend

- Python 3.12+
- FastAPI、Pydantic、SQLAlchemy 2.0、Alembic
- PostgreSQL（平台元数据）
- SQLGlot
- Wren Core、Vanna（Adapter）
- APScheduler（轻量任务，按需）

### Frontend (Studio)

- Vue 3、TypeScript、Vite、Element Plus、Pinia、Vue Router、Axios
- Monaco Editor（MDL/SQL）
- Vue Flow（关系图；可放 Phase 1 末或 Phase 2）
- **ChatBI 可视化**：**markdown-it** + **markdown-it-gpt-vis** + **@antv/gpt-vis**
- **不默认引入 ECharts**

### Deploy

- Docker / Docker Compose（PostgreSQL + API + Web）

## 8. Domain Model (Metadata)

- `Project` / `User` / `Role` / `Membership`
- `DataSource`（加密凭证、类型、只读标记）
- `SemanticModel` / `Metric` / `GlossaryTerm` / `MdlRevision`（草稿 → 发布）
- `Integration` / `RawOpenApiSpec` / `ToolSemanticOverlay`（源与语义分离；同步不覆盖 Overlay）
- `Capability`（kind、input/output schema、status、source_ref、governance）
- `QueryRun` / `ToolInvocation` / `AuditEvent`

## 9. Key Data Flows

### 9.1 Semantic Query

User question → semantic context → Wren compile SQL → SQLGlot read-only validate → read-only execute → format → `QueryRun` audit

### 9.2 Text-to-SQL

User question → schema/example retrieval → Vanna generate → SQLGlot validate → read-only execute → audit  

Published metric definitions win over AI-generated SQL when definitions conflict.

### 9.3 Functional / Hybrid (Phase 3)

User question → Capability Discovery → optional semantic query → Executor calls approved read-only API → aggregate + explain → audit

### 9.4 ChatBI rendering (Phase 2+)

1. Model/API returns Markdown (prose + optional ` ```sql ` + ` ```GPT-Vis ` fences).  
2. Studio `MarkdownMessage` uses `markdown-it` + `gptVisMarkdownItPlugin`（插件须在高亮插件之前）。  
3. Plugin emits `<gpt-vis>` Web Component；browser mounts `@antv/gpt-vis` and `render()`s Syntax.  
4. Fence language tag is **`GPT-Vis`**; body starts with `vis <chart-type>`.  
5. Streaming: re-render accumulated Markdown; prefer reusing chart instances; incomplete fences show as code/placeholder until complete.  
6. Sanitize HTML; whitelist `gpt-vis` and required attributes.  
7. Primary path is Markdown fences (not a separate `vis_syntax` field). Optional structured `chart_spec` is non-MVP debug only.

## 10. Security & Error Handling

### SQL

- Read-only DB credentials
- Single-statement execution
- AST validation / deny list
- Timeout + max rows
- Restrict system catalogs / sensitive fields

### API / MCP

- Import as draft; human confirm no side effects before publish
- Destination host allowlist (SSRF)
- Timeout + response size limits
- Encrypted credentials; redact secrets in logs

### Capability governance

- Approval + publication required for execution in production paths
- Actor authorization (user/agent)
- Full audit of tool/SQL/API invocations

### API errors

Unified envelope: `code`, `message`, `request_id`, optional `details`.

### Degradation

- Semantic failure may optionally fall back to Text-to-SQL when policy allows; execution summary must show which path ran.
- Unpublished / non-read-only / unauthorized capability → hard deny.
- Source timeouts fail closed (no unsafe blind retry of side-effect-uncertain calls).

## 11. Repository Layout (target)

Align with README:

```text
apps/api, apps/mcp, apps/worker
semantix/{core,datasource,semantic,capability,integrations,engines,query,knowledge,agent,mcp,security,evolution,audit,models}
web/   # Semantix Studio
mdl/, migrations/, tests/, deployments/, docs/
```

Current repo state: README + LICENSE primarily; implementation starts from scaffold.

## 12. Testing Strategy

- Unit: SQLGlot policy, capability state machine, Overlay merge, markdown-it GPT-Vis fence transform helpers
- Integration: datasource discovery, one Wren/Vanna path against fixture DB
- E2E smoke: login → create datasource → ChatBI question with Markdown + chart fence

## 13. Risks

| Risk | Mitigation |
|---|---|
| Wren/Vanna integration cost | Strict adapters; fixture SQL path to protect Phase 2 acceptance |
| Incomplete GPT-Vis fences while streaming | Tolerant placeholder + final full render |
| Scope creep into Agent/MCP early | Hard stop after Phase 3 for MVP plan |
| TDengine dialect gaps | PG first; MySQL/TDengine follow without blocking main path |

## 14. Decisions Log

| Decision | Choice |
|---|---|
| Plan scope | B：全路线图 + Phase 0–3 细计划 |
| Delivery style | 纵向切片 |
| Mutation | 全平台只读 |
| ChatBI charts | `@antv/gpt-vis` + `markdown-it` + `markdown-it-gpt-vis` |
| ECharts | 默认不引入 |
| Agent framework | Phase 3 简化 Planner；Phase 5 Pydantic AI Adapter |
| Frontend framework | Vue 3 |

## 15. Next Step

After this spec is approved, write implementation plan:

`docs/superpowers/plans/2026-11-06-semantix-phase0-3.md`

（含 Phase 0–7 里程碑摘要 + Phase 0–3 任务级步骤。）
