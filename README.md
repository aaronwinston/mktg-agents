<img width="1082" height="607" alt="Screenshot 2026-04-26 at 9 18 56 PM" src="https://github.com/user-attachments/assets/e712f82b-f49a-47f8-9cef-37784dafd509" />


## What is ForgeOS

ForgeOS is a **local-first marketing command center** that wraps a markdown-based "engine" of voice rules, skills, playbooks, and context with a Next.js cockpit. You use it to produce developer marketing at the throughput of a small team. The markdown directories at the repo root (`core/`, `context/`, `skills/`, `playbooks/`, `rubrics/`, `briefs/`, `prompts/`) are the system's brain and remain canonical — the app reads from and writes to them. The database (SQLite via SQLModel) holds runtime state only: projects, folders, deliverables, briefs, chat sessions and messages, scrape items, and pipeline run state.

---

## How to run

### Prerequisites

- Python 3.9+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### Backend (API)

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Then start the API:
```bash
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Check `/api/health` to confirm it's up.

### Frontend (Web App)

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`. The dashboard loads instantly — quote, layout, and nav are all static. Data comes from the local API.

---

## Architecture overview

ForgeOS has two run modes:

### Chat mode
Conversational, optionally producing a brief first, optionally executing a playbook to produce a deliverable. This is the primary path. You interact with the system in `/workspace`, where you can chat, edit briefs, and manage deliverables. Backed by `ChatSession`, `ChatMessage`, `Brief`, `Deliverable` in the database.

### Pipeline mode
Fire-and-forget execution of the full agent chain against a single prompt. The system runs 11 specialized agents in sequence, each reading the brief and the previous agent's output, then passing an improved draft forward. Backed by `PipelineRun` in the database. Legacy "Sessions" UI.

Both modes exist for different reasons and both remain. Choose chat for interactive work; choose pipeline for batch production.

---

## The markdown engine

The `core/`, `context/`, `skills/`, `playbooks/`, `rubrics/` directories at repo root are the system's **canonical source of truth**. Every agent reads from these before running. You own and control these files.

### core/
Load-bearing doctrine. You edit these from the Settings page (explicit save required):
- `VOICE.md` — your brand voice, tone, audience POV
- `STYLE_GUIDE.md` — formatting, conventions, visual style
- `CLAIMS_POLICY.md` — what claims are safe, what needs evidence, what's off-limits

### context/
Narrative, strategy, and execution layers. Composable per brief. Thin by design in v1 (Aaron's intention — needs expansion later):
- `00_orchestration/` — context routing instructions for agents
- `01_philosophy/` — marketing principles (developer relations, positioning)
- `02_narrative/` — messaging frameworks, competitive POV, campaign messaging
- `03_strategy/` — content strategy, audience insights
- `04_execution/` — campaign blueprints, launch playbooks
- `05_patterns/` — proven content patterns
- `06_influence/` — analyst relations strategy
- `07_research/` — market research playbooks, intelligence scoring prompt

**Which context layers are thin?** `02_narrative/` (messaging frameworks, competitive POV, campaign messaging), `03_strategy/` (content strategy), and `04_execution/` (launch frameworks) are placeholder-scale. PMM-led expansion here will unlock better output. Document in Settings which files need growth and how to expand them.

### skills/
11 agent definitions, organized by category. Each has a `SKILL.md` that defines the agent's role, constraints, and process. Read them to understand what each agent does. Agents load their own SKILL.md before running — change the file, change the agent.

### playbooks/
Agent orchestration specs. Define the order of agents, the context layers to use, and the branching logic for different content types. Composable with named context layers.

### rubrics/
Scoring guidance. Used for draft quality assessment and content filtering. Editable from Settings.

---

## Scrape schedule

The system runs a scraper twice daily (configurable via cron). It reads from:
- Hacker News (Algolia API)
- GitHub (topics RSS)
- ArXiv (RSS)
- Reddit (JSON API)
- Generic RSS feeds (configured in Settings)

Each item gets a score (≥7 for inclusion in briefing). The synthesis pass (why_relevant, content_angle) runs once per scrape, not on every dashboard load. The Briefing Book shows curated items from the last 24 hours; the Intelligence page shows the full scored feed.

---

## Empty context layers (intentional for v1)

The narrative layer (`context/02_narrative/`) contains three thin placeholder files:
- `messaging-framework.md` — needs ~10x expansion
- `competitive-pov.md` — placeholder
- `campaign-messaging.md` — placeholder

Similarly, `context/03_strategy/ar-strategy.md` and `context/04_execution/` are thin. These are not bugs — Aaron's intention for v1 is to ship with a strong voice/style/claims foundation and thin narrative/strategy layers. You'll expand them as your team uses the system.

**How to expand them:**
1. Open Settings → Engine tree
2. Navigate to the relevant context file
3. Edit it directly (markdown editor, explicit save required)
4. The next pipeline run or brief generation will use the new content

---

## Contributing

### Adding a skill

1. Create `skills/{category}/{agent-name}/SKILL.md`
2. Define role, constraints, input/output shape
3. Reference it in a playbook or use it as a standalone agent in chat

### Adding a context layer

1. Create `context/{layer_number}_{name}/{file}.md`
2. Reference it by path in the orchestrator or playbook
3. Use it to compose briefs or pipeline runs

### Adding a playbook

1. Create `playbooks/{content_type}.md`
2. Define the agent order, context layers, branching logic
3. Reference it in chat toggles or pipeline runs

### Style guide

Read `core/VOICE.md`. All contributions should match the voice and style defined there.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.9+ |
| Database | SQLite (via SQLModel) |
| LLM | Anthropic Claude (Opus for generation, Haiku for scoring) |
| Frontend | Next.js 14 + TypeScript |
| Styling | Tailwind CSS |
| Data fetching | React Query |
| Observability | Arize AX (OpenTelemetry) |

**No cloud database. No auth service. No Redis.** SQLite on disk. One API key. One person can run it.

---

## v1 Release Status

ForgeOS v1 (phases 1–4 of FORGEOS_PRD.md) is production-ready. Key components:

### 4.1 Showstopper fixes ✅
- API health endpoint (`GET /api/health`)
- Model configuration (Claude Opus for generation, Haiku for scoring)
- Error handling: frontend distinguishes API unreachable, HTTP errors, and empty data states

### 4.2–4.4 Unified execution pipeline ✅
- Single agent chain execution path via `execute_playbook()`
- Pipeline step persistence: each agent's input/output logged to DB
- Final output persisted to Deliverable on pipeline completion

### 4.3 Intelligence unification ✅
- Briefing Book: curated ScrapeItem view (score ≥7, last 24h, with why_relevant + content_angle)
- Intelligence page: full scored feed with filters
- Refresh button triggers `/api/intelligence/scrape` and reloads briefing

### 4.4 PipelineRun refactor ✅
- Model properly links Brief → PipelineRun → Deliverable
- Output lives on Deliverable.body_md, not PipelineRun.output
- Sessions UI displays run state + progress

### 4.5 Workspace surface ✅
- Three-pane layout: project tree (left), chat/editor/brief tabs (center), toggles + context (right)
- Full CRUD for projects/folders/deliverables
- TipTap markdown editor with round-trip fidelity
- Streaming chat with Claude integration

### 4.6 Settings/Engine editor ✅
- Tree view for core/, context/, skills/, playbooks/, rubrics/
- WYSIWYG markdown editor with frontmatter support
- References indicator shows skills/playbooks using each file
- Unsaved changes warning (browser + UI level)
- Explicit save with error handling

### 4.7–4.8 Frontend polish ✅
- React Query for data fetching (chosen; SWR not present)
- All async surfaces have loading/empty/error states
- Documentation updated

---

## License

MIT. Use it, fork it, build on it.
