# Phases 4–7 — stubs only

Detailed plans will be written separately. Pointers from Phase 0–3 MVP:

## Phase 4 — MCP

- `apps/mcp` FastMCP server exposing **published** capabilities only
- MCP Client connection + draft import + Studio MCP pages
- Acceptance: external MCP client lists/calls `query_metric` / `get_device_alarms`

## Phase 5 — Agent Studio

- Pydantic AI adapter under `semantix/agent/adapters/`
- Agent config, tool allowlists, step/timeout limits, traces UI
- Acceptance: Business Analyst template hybrid run with visible trace

## Phase 6 — Knowledge + Evolution

- Document ingest, embeddings, SQL examples
- Candidate metrics/terms from query logs; human publish only
- Acceptance: retrieval helps ChatBI; published metrics unchanged without approval

## Phase 7 — Productization

- Full RBAC matrix, secrets UX, monitoring pages, prod compose/images
- Acceptance: deploy checklist + audit completeness

See also: `docs/superpowers/plans/2026-11-06-semantix-phase0-3.md` (Phases 4–7 section) and `docs/superpowers/specs/2026-11-06-semantix-mvp-design.md`.
