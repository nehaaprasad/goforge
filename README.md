# GoForge

GoForge (repository **goforge**) is an AI-assisted engineering workflow platform. Its first product surface, **PatchFlow**, converts natural-language tickets into validated pull requests for Go monorepos.

The system is designed around **clarity, safety, and reviewability**:
- plan the work first
- generate minimal diff-oriented changes
- generate tests for the changed behavior
- validate with Go toolchain checks before PR creation

---

## Vision

PatchFlow (within GoForge) acts as a developer cockpit for ticket-to-PR automation:

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
  frontend/         # PatchFlow marketing + UI shell (implemented)
  backend/          # FastAPI orchestration API (skeleton + mock pipeline)
  sandbox-repo/     # Local Go repo target for the first vertical slice
```

Planned expansion (later phases):

```text
goforge/
  backend/
    goforge/        # Python package (current)
    # future: agents/, rag/, validation/, github/ modules as logic grows
```

---

## Frontend (Implemented)

The frontend includes:

1. **Marketing site** (`/`) — premium dark-first landing page with:
   - Header (logo, nav, CTAs)
   - Hero section (headline, subheadline, CTAs, product mockup)
   - Trust strip
   - How-it-works section
   - Feature grid
   - Demo preview section
   - Architecture flow section
   - FAQ
   - Final CTA
   - Footer

2. **Live workflow** (`/workflow`) — connects to the FastAPI backend:
   - task input + Run → `POST /api/run`
   - live steps, logs, and unified diff via `GET /api/run/{id}` and SSE `…/stream`

Configure the API URL for the browser:

```bash
# frontend/.env.local (optional; defaults to http://127.0.0.1:8000)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The landing mockups reflect the same PatchFlow layout model:
- left: workflow steps/statuses
- center: diff viewer
- right: agent/log stream

---

## Backend (Implemented — Phase B skeleton)

The backend is a FastAPI service that owns run lifecycle and exposes the API contracts the UI will consume.

### What works today
- `POST /api/run` creates a run against the local repo path and runs a **hybrid** pipeline: early stages are **mock** (Planner → Test Generation), then **Validation** applies the proposed **unified diff** with **`git apply`** (after initializing a local git baseline in `sandbox-repo` on first use), runs **`go test ./...`**, then **resets** the worktree to `HEAD` so the next run starts clean.
- `GET /api/run/{id}` returns the latest snapshot (steps, logs, mock diff, errors).
- `GET /api/run/{id}/stream` streams **SSE** snapshots as the pipeline advances.
- `GET /health` reports whether `./sandbox-repo` exists on disk.
- `GET /api/pr/{id}` returns **501** until GitHub integration exists.
- If **`go test ./...` fails**, the run ends in **`failed`** with Validation marked **`failed`** and logs containing the `go test` output.

### Configuration
- `GOFORGE_REPO_ROOT`: absolute or relative path to the local Go repo (default: repository `sandbox-repo/` next to this README).

### Run locally
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn goforge.main:app --reload --host 127.0.0.1 --port 8000
```

### Backend tests
```bash
cd backend
.venv/bin/python -m unittest discover -s tests -v
```

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

## API (current + planned)

Implemented:
- `POST /api/run` — start run, return run ID
- `GET /api/run/{id}` — run snapshot
- `GET /api/run/{id}/stream` — SSE stream of snapshots
- `GET /health` — repo path probe

Stub:
- `GET /api/pr/{id}` — returns `501` until PR automation ships

---

## Local Development

### Prerequisites
- Node.js 20+
- npm
- Python 3.11+ (for backend)

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

### Phase B (In progress / baseline done)
- FastAPI backend skeleton
- run lifecycle + in-memory store
- mock pipeline + SSE stream
- frontend `/workflow` page wired to the API (dev)

### Phase C (In progress / baseline done)
- local `./sandbox-repo` Go module + **git apply** of mock diff + **`go test ./...`** + worktree reset
- next: **real agent diffs**, **retry/fix** loop, then **PR automation**

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

- `sandbox-repo/` is a **small real Go module** (see `go.mod` and `internal/greet/`) so `go test ./...` can pass in the Validation stage.
- On first pipeline run, the backend may **`git init`** that directory (ignored by git via `sandbox-repo/.git/` in `.gitignore`) so patches can be applied and reverted safely.
- Planner/code/test agents remain **mock** until LLM integration; **patch apply + go test** are real.
