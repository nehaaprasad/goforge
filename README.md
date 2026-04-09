# GoForge

GoForge (repository **goforge**) is an AI-assisted engineering workflow platform. Its first product surface, **PatchFlow**, converts natural-language tickets into validated pull requests for Go monorepos.

The system is designed around **clarity, safety, and reviewability**:
- plan the work first
- generate minimal diff-oriented changes
- generate tests for the changed behavior
- validate with Go toolchain checks before PR creation

---

<svg aria-roledescription="flowchart-v2" role="graphics-document document" viewBox="-8 -8 850.1328125 235.2376251220703" style="max-width: 850.1328125px;" xmlns="http://www.w3.org/2000/svg" width="100%" id="mermaid-svg-1775736862542-fzaxm3bzs"><style>#mermaid-svg-1775736862542-fzaxm3bzs{font-family:"trebuchet ms",verdana,arial,sans-serif;font-size:16px;fill:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .error-icon{fill:#141414;}#mermaid-svg-1775736862542-fzaxm3bzs .error-text{fill:#e34671;stroke:#e34671;}#mermaid-svg-1775736862542-fzaxm3bzs .edge-thickness-normal{stroke-width:2px;}#mermaid-svg-1775736862542-fzaxm3bzs .edge-thickness-thick{stroke-width:3.5px;}#mermaid-svg-1775736862542-fzaxm3bzs .edge-pattern-solid{stroke-dasharray:0;}#mermaid-svg-1775736862542-fzaxm3bzs .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-svg-1775736862542-fzaxm3bzs .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-svg-1775736862542-fzaxm3bzs .marker{fill:rgba(228, 228, 228, 0.92);stroke:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .marker.cross{stroke:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs svg{font-family:"trebuchet ms",verdana,arial,sans-serif;font-size:16px;}#mermaid-svg-1775736862542-fzaxm3bzs .label{font-family:"trebuchet ms",verdana,arial,sans-serif;color:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .cluster-label text{fill:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .cluster-label span,#mermaid-svg-1775736862542-fzaxm3bzs p{color:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .label text,#mermaid-svg-1775736862542-fzaxm3bzs span,#mermaid-svg-1775736862542-fzaxm3bzs p{fill:rgba(228, 228, 228, 0.92);color:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .node rect,#mermaid-svg-1775736862542-fzaxm3bzs .node circle,#mermaid-svg-1775736862542-fzaxm3bzs .node ellipse,#mermaid-svg-1775736862542-fzaxm3bzs .node polygon,#mermaid-svg-1775736862542-fzaxm3bzs .node path{fill:#181818;stroke:#454545;stroke-width:1px;}#mermaid-svg-1775736862542-fzaxm3bzs .flowchart-label text{text-anchor:middle;}#mermaid-svg-1775736862542-fzaxm3bzs .node .label{text-align:center;}#mermaid-svg-1775736862542-fzaxm3bzs .node.clickable{cursor:pointer;}#mermaid-svg-1775736862542-fzaxm3bzs .arrowheadPath{fill:#e7e7e7;}#mermaid-svg-1775736862542-fzaxm3bzs .edgePath .path{stroke:rgba(228, 228, 228, 0.92);stroke-width:2.0px;}#mermaid-svg-1775736862542-fzaxm3bzs .flowchart-link{stroke:rgba(228, 228, 228, 0.92);fill:none;}#mermaid-svg-1775736862542-fzaxm3bzs .edgeLabel{background-color:#18181899;text-align:center;}#mermaid-svg-1775736862542-fzaxm3bzs .edgeLabel rect{opacity:0.5;background-color:#18181899;fill:#18181899;}#mermaid-svg-1775736862542-fzaxm3bzs .labelBkg{background-color:rgba(24, 24, 24, 0.5);}#mermaid-svg-1775736862542-fzaxm3bzs .cluster rect{fill:rgba(64, 64, 64, 0.47);stroke:#454545;stroke-width:1px;}#mermaid-svg-1775736862542-fzaxm3bzs .cluster text{fill:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs .cluster span,#mermaid-svg-1775736862542-fzaxm3bzs p{color:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:"trebuchet ms",verdana,arial,sans-serif;font-size:12px;background:rgba(64, 64, 64, 0.6);border:1px solid #454545;border-radius:2px;pointer-events:none;z-index:100;}#mermaid-svg-1775736862542-fzaxm3bzs .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgba(228, 228, 228, 0.92);}#mermaid-svg-1775736862542-fzaxm3bzs :root{--mermaid-font-family:"trebuchet ms",verdana,arial,sans-serif;}</style><g><marker orient="auto" markerHeight="12" markerWidth="12" markerUnits="userSpaceOnUse" refY="5" refX="6" viewBox="0 0 10 10" class="marker flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd"><path style="stroke-width: 1; stroke-dasharray: 1, 0;" class="arrowMarkerPath" d="M 0 0 L 10 5 L 0 10 z"/></marker><marker orient="auto" markerHeight="12" markerWidth="12" markerUnits="userSpaceOnUse" refY="5" refX="4.5" viewBox="0 0 10 10" class="marker flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointStart"><path style="stroke-width: 1; stroke-dasharray: 1, 0;" class="arrowMarkerPath" d="M 0 5 L 10 10 L 10 0 z"/></marker><marker orient="auto" markerHeight="11" markerWidth="11" markerUnits="userSpaceOnUse" refY="5" refX="11" viewBox="0 0 10 10" class="marker flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-circleEnd"><circle style="stroke-width: 1; stroke-dasharray: 1, 0;" class="arrowMarkerPath" r="5" cy="5" cx="5"/></marker><marker orient="auto" markerHeight="11" markerWidth="11" markerUnits="userSpaceOnUse" refY="5" refX="-1" viewBox="0 0 10 10" class="marker flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-circleStart"><circle style="stroke-width: 1; stroke-dasharray: 1, 0;" class="arrowMarkerPath" r="5" cy="5" cx="5"/></marker><marker orient="auto" markerHeight="11" markerWidth="11" markerUnits="userSpaceOnUse" refY="5.2" refX="12" viewBox="0 0 11 11" class="marker cross flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-crossEnd"><path style="stroke-width: 2; stroke-dasharray: 1, 0;" class="arrowMarkerPath" d="M 1,1 l 9,9 M 10,1 l -9,9"/></marker><marker orient="auto" markerHeight="11" markerWidth="11" markerUnits="userSpaceOnUse" refY="5.2" refX="-1" viewBox="0 0 11 11" class="marker cross flowchart" id="mermaid-svg-1775736862542-fzaxm3bzs_flowchart-crossStart"><path style="stroke-width: 2; stroke-dasharray: 1, 0;" class="arrowMarkerPath" d="M 1,1 l 9,9 M 10,1 l -9,9"/></marker><g class="root"><g class="clusters"><g id="server" class="cluster default flowchart-label"><rect height="219.2376251220703" width="547.8359375" y="0" x="286.296875" ry="0" rx="0" style=""/><g transform="translate(560.21484375, 0)" class="cluster-label"><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">Your machine or server</tspan></text></g></g><g id="browser" class="cluster default flowchart-label"><rect height="118" width="150.9375" y="37.30940628051758" x="0" ry="0" rx="0" style=""/><g transform="translate(75.46875, 37.30940628051758)" class="cluster-label"><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">Browser</tspan></text></g></g></g><g class="edgePaths"><path marker-end="url(#mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd)" style="fill:none;" class="edge-thickness-normal edge-pattern-solid flowchart-link LS-UI LE-API" id="L-UI-API-0" d="M125.938,88.938L130.104,87.916C134.271,86.895,142.604,84.852,158.051,83.831C173.497,82.809,196.057,82.809,218.617,82.809C241.177,82.809,263.737,82.809,278.317,83.463C292.897,84.116,299.498,85.423,302.798,86.077L306.098,86.731"/><path marker-end="url(#mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd)" style="fill:none;" class="edge-thickness-normal edge-pattern-solid flowchart-link LS-API LE-Pipeline" id="L-API-Pipeline-0" d="M409.728,85.309L420.297,79.675C430.866,74.04,452.003,62.77,465.855,57.135C479.707,51.5,486.274,51.5,489.557,51.5L492.841,51.5"/><path marker-end="url(#mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd)" style="fill:none;" class="edge-thickness-normal edge-pattern-solid flowchart-link LS-Pipeline LE-Repo" id="L-Pipeline-Repo-0" d="M647.539,51.5L651.706,51.5C655.872,51.5,664.206,51.5,671.656,51.5C679.106,51.5,685.672,51.5,688.956,51.5L692.239,51.5"/><path marker-end="url(#mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd)" style="fill:none;" class="edge-thickness-normal edge-pattern-solid flowchart-link LS-API LE-DB" id="L-API-DB-0" d="M409.728,117.309L420.297,122.944C430.866,128.579,452.003,139.849,470.015,145.484C488.026,151.119,502.912,151.119,510.355,151.119L517.798,151.119"/><path marker-end="url(#mermaid-svg-1775736862542-fzaxm3bzs_flowchart-pointEnd)" style="fill:none;" class="edge-thickness-normal edge-pattern-solid flowchart-link LS-UI LE-API" id="L-UI-API-1" d="M125.938,113.681L130.104,114.702C134.271,115.724,142.604,117.767,158.051,118.788C173.497,119.809,196.057,119.809,218.617,119.809C241.177,119.809,263.737,119.809,278.317,119.156C292.897,118.502,299.498,117.195,302.798,116.542L306.098,115.888"/></g><g class="edgeLabels"><g transform="translate(218.6171875, 82.80940628051758)" class="edgeLabel"><g transform="translate(-39.03125, -8.5)" class="label"><rect height="17.000234603881836" width="77.9960708618164" ry="0" rx="0"/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">POST task</tspan></text></g></g><g class="edgeLabel"><g transform="translate(0, 0)" class="label"><rect height="0" width="0" ry="0" rx="0"/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve"/></text></g></g><g class="edgeLabel"><g transform="translate(0, 0)" class="label"><rect height="0" width="0" ry="0" rx="0"/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve"/></text></g></g><g class="edgeLabel"><g transform="translate(0, 0)" class="label"><rect height="0" width="0" ry="0" rx="0"/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve"/></text></g></g><g transform="translate(218.6171875, 119.80940628051758)" class="edgeLabel"><g transform="translate(-42.6796875, -8.5)" class="label"><rect height="17.000234603881836" width="85.28243255615234" ry="0" rx="0"/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">SSE stream</tspan></text></g></g></g><g class="nodes"><g transform="translate(379.71875, 101.30940628051758)" id="flowchart-API-1" class="node default default flowchart-label"><rect height="32" width="136.84375" y="-16" x="-68.421875" ry="0" rx="0" style="" class="basic label-container"/><g transform="translate(0, -8.5)" style="" class="label"><rect/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">FastAPI backend</tspan></text></g></g><g transform="translate(572.83984375, 51.5)" id="flowchart-Pipeline-2" class="node default default flowchart-label"><rect height="33" width="149.3984375" y="-16.5" x="-74.69921875" ry="0" rx="0" style="" class="basic label-container"/><g transform="translate(0, -9)" style="" class="label"><rect/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">PatchFlow pipeline</tspan></text></g></g><g transform="translate(753.3359375, 51.5)" id="flowchart-Repo-3" class="node default default flowchart-label"><rect height="33" width="111.59375" y="-16.5" x="-55.796875" ry="0" rx="0" style="" class="basic label-container"/><g transform="translate(0, -9)" style="" class="label"><rect/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">Git + Go repo</tspan></text></g></g><g transform="translate(572.83984375, 151.11881256103516)" id="flowchart-DB-4" class="node default default flowchart-label"><path transform="translate(-49.7421875,-33.11881394863228)" d="M 0,11.079209299088188 a 49.7421875,11.079209299088188 0,0,0 99.484375 0 a 49.7421875,11.079209299088188 0,0,0 -99.484375 0 l 0,44.07920929908819 a 49.7421875,11.079209299088188 0,0,0 99.484375 0 l 0,-44.07920929908819" style=""/><g transform="translate(0, -9)" style="" class="label"><rect/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">SQLite runs</tspan></text></g></g><g transform="translate(75.46875, 101.30940628051758)" id="flowchart-UI-0" class="node default default flowchart-label"><rect height="32" width="100.9375" y="-16" x="-50.46875" ry="0" rx="0" style="" class="basic label-container"/><g transform="translate(0, -8.5)" style="" class="label"><rect/><text style=""><tspan class="row" x="0" dy="1em" xml:space="preserve">Workflow UI</tspan></text></g></g></g></g></g></svg>


  
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

## Backend (Implemented)

The backend is a FastAPI service that owns run lifecycle and exposes the API contracts the UI will consume.

### What works today
- `POST /api/run` creates a run against the local repo path and runs the **PatchFlow pipeline**: **Planner** → **Context Retrieval** (**RAG**: chunk `.go` files, **embeddings**, **top‑k** cosine retrieval when `GOFORGE_OPENAI_API_KEY` is set, prepended to the bounded **full-file** bundle) → **Code Generation** (unified diff + **`notes`**, mock or LLM JSON) → **Test Generation** (structured **`tests`** paths + **`coverage_focus`**, mock or LLM JSON) → **Validation** (`git apply` + `go build ./...` + `go test ./...`). **After initializing** a local git baseline in `sandbox-repo` on first use, each run **resets** to `HEAD` before applying, then **resets** again after the run so the next run starts clean.
- With an API key, **Validation** can **retry** up to `GOFORGE_VALIDATION_MAX_ATTEMPTS` times (default 3) on the same run, feeding the previous failure back into the code agent.
- `GET /api/run/{id}` returns the latest snapshot (steps, logs, diff, **`code_notes`**, **`test_paths`**, **`coverage_focus`**, `pr_url`, errors).
- `GET /api/run/{id}/stream` streams **SSE** snapshots as the pipeline advances.
- `GET /health` reports whether `./sandbox-repo` exists on disk and whether **`go`** and **`git`** are on `PATH` (with version lines).
- `GET /api/pr/{id}` returns **run status**, **`pr_url`** (if a PR was opened), and **`error`** (if any). PR creation is **optional** (see GitHub below).
- If **`go build ./...`** or **`go test ./...`** fails after retries are exhausted, the run ends in **`failed`** with Validation marked **`failed`** and logs containing the failing output.

### Configuration
- `GOFORGE_REPO_ROOT`: absolute or relative path to the local Go repo (default: repository `sandbox-repo/` next to this README).

**Optional LLM** (OpenAI-compatible Chat Completions JSON): when `GOFORGE_OPENAI_API_KEY` is set, **Planner**, **Code Generation**, and **Test Generation** call the API; otherwise the planner uses a deterministic mock plan, codegen uses a fixed sandbox **mock diff** (see `backend/goforge/default_diff.py`), and the test agent uses heuristics from the diff. Planner failures fall back to mock output with a **risk** line; codegen/test failures fall back to mock output with a log line. See `backend/.env.example` for timeouts and models.

**Optional GitHub PR** (after `go build` and `go test` pass): set `GOFORGE_GITHUB_TOKEN` (repo scope) and `GOFORGE_GITHUB_REPO` as `owner/name`. The backend creates a branch, commits, pushes to `https://github.com/owner/name`, and opens a PR via the GitHub API. Leave unset to skip (logs will say so). Set `GOFORGE_GITHUB_DEFAULT_BRANCH` only if auto-detection does not match your default branch (empty = detect `main` vs `master` locally).

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

### Production notes
- **Run persistence**: snapshots are written to **SQLite** at `GOFORGE_DB_PATH` (default `backend/data/goforge.db`). After a restart, **`GET /api/run/{id}`** still returns completed/failed runs. In-flight runs (`queued` / `running`) are marked **failed** with *Run interrupted by server restart.*
- **Disable persistence** (e.g. tests): `GOFORGE_PERSISTENCE_ENABLED=false`.
- **Health**: `GET /health` includes `persistence`, `database_path`, and `openai_key_configured`.
- **Docker**: from the repo root, `docker compose up --build` runs the API with `./sandbox-repo` mounted and a volume for `/data` (see `docker-compose.yml`). Install **Go** inside the image so `go build` / `go test` validation works without relying on the host.

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
- `GET /api/pr/{id}` — run snapshot fields for PR (`pr_url`, `status`, `error`)

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
- Planner/code/test agents remain **mock** until LLM integration; **patch apply + go build + go test** are real.
