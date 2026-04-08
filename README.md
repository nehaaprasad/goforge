# GoForge

 GoForge is an AI-assisted engineering workflow that converts natural-language tickets into validated pull requests for Go monorepos.

The system is designed around **clarity, safety, and reviewability**:
- plan the work first
- generate minimal diff-oriented changes
- generate tests for the changed behavior
- validate with Go toolchain checks before PR creation

---

## Vision

GoForge acts as a developer cockpit for ticket-to-PR automation:

`Ticket -> Planner -> Context Retrieval -> Code Agent -> Test Agent -> Validation -> PR`

It is intentionally built with strict stage boundaries and machine-readable contracts to avoid hidden behavior and reduce risk.

---

## Current Scope (Vertical Slice)

This repository currently targets a **single local monorepo workflow** for fast iteration:

- repository source is a local filesystem path
- no git clone from URL yet
- no external network dependency required for the first slice
- sandbox target repository path is `./sandbox-repo`

Remote repository ingestion and clone support are planned for a later phase.

---

## Tech Stack

### Frontend
- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- shadcn-style UI components

### Planned Backend (orchestration engine)
- Python + FastAPI

### Target codebase
- Go monorepo (modified by generated patches/diffs)

---

## Repository Structure

```text
goforge/
  frontend/         # PatchFlow landing + UI shell (implemented)
  sandbox-repo/     # Local Go repo target for first vertical slice
```

As backend orchestration is added, expected top-level structure:

```text
goforge/
  frontend/
  backend/
    api/
    agents/
    rag/
    validation/
    github/
  sandbox-repo/
```

---

## Frontend (Implemented)

The frontend is implemented as a premium dark-first product landing page with:

1. Header (logo, nav, CTAs)
2. Hero section (headline, subheadline, CTAs, product mockup)
3. Trust strip
4. How-it-works section
5. Feature grid
6. Demo preview section
7. Architecture flow section
8. FAQ
9. Final CTA
10. Footer

The mockups reflect the intended PatchFlow app model:
- left: workflow steps/statuses
- center: diff viewer
- right: agent/log stream

---

## Planned Backend Workflow

### Stage Pipeline
1. Receive task from frontend
2. Create run ID
3. Planner agent produces structured plan
4. Context retrieval gathers relevant Go code
5. Code agent proposes minimal diff
6. Test agent proposes/adds tests
7. Validation runs `go build` and `go test`
8. PR is created only on successful validation

### Core Principles
- strict JSON contracts between stages
- explicit run states (`queued`, `running`, `done`, `failed`)
- visible logs and validation results
- no hidden auto-merge behavior

---

## API Shape (Planned)

- `POST /api/run` -> start run, return run ID
- `GET /api/run/:id` -> run state + aggregated output
- `GET /api/run/:id/stream` -> live updates (logs/status)
- `GET /api/pr/:id` -> PR details when available

---

## Local Development

### Prerequisites
- Node.js 20+
- npm

### Run frontend
```bash
cd frontend
npm install
npm run dev
```

### Quality checks
```bash
cd frontend
npm run lint
npm run build
```

---

## Roadmap

### Phase A (Done)
- frontend layout and storytelling surface
- product mock sections aligned to orchestrator workflow

### Phase B
- FastAPI backend skeleton
- run lifecycle state manager
- mock run stream to frontend

### Phase C
- planner -> code -> test pipeline integration
- local `./sandbox-repo` operations
- validation loop with Go checks

### Phase D
- branch/commit/PR automation
- retry/fix loop for validation failures

### Phase E
- error handling polish
- production hardening and observability
- optional remote repository ingestion

---

## Design and Quality Standards

PatchFlow development follows these constraints:
- clean, readable, maintainable code
- clear naming and logical structure
- explicit edge-case handling
- minimal but meaningful comments
- no unnecessary abstractions
- validation-first automation

---

## Notes

- `sandbox-repo/` is intentionally committed as a placeholder for local-target execution in this first slice.
- The frontend is ready for iterative refinement while backend orchestration is added.
