# ForgeOS API

FastAPI backend for ForgeOS. Serves as the interface between the markdown engine, the SQLite database, and the web frontend.

## Setup

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your configuration:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL_GENERATION=claude-opus-4-7
MODEL_SCORING=claude-haiku-4-5
DATABASE_URL=sqlite:///./forgeos.db
ARIZE_SPACE_ID=your_space_id_here
ARIZE_API_KEY=your_arize_api_key_here
```

- `ANTHROPIC_API_KEY` — Required. Get from [console.anthropic.com](https://console.anthropic.com/)
- `MODEL_GENERATION` — Model for content generation (default: `claude-opus-4-7`)
- `MODEL_SCORING` — Model for intelligence scoring (default: `claude-haiku-4-5`)
- `ARIZE_SPACE_ID`, `ARIZE_API_KEY` — Optional. Observability tracing via Arize AX

## Running

```bash
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Check `/api/health` for a health ping.

## API Overview

### Health & Status

- `GET /api/health` — Health check

### Content Organization

- `GET /api/projects` — List all projects
- `POST /api/projects` — Create a project
- `GET /api/folders` — List folders in a project
- `POST /api/folders` — Create a folder
- `GET /api/deliverables` — List deliverables
- `POST /api/deliverables` — Create a deliverable
- `GET /api/deliverables/{id}` — Get deliverable details

### Brief Management

- `GET /api/briefs` — List briefs
- `POST /api/briefs` — Create a brief
- `GET /api/briefs/{id}` — Get brief details
- `PUT /api/briefs/{id}` — Update a brief

### Chat (Interactive Mode)

- `POST /api/chat/brief` — Generate a brief from a prompt
- `POST /api/chat/generate` — Generate content using a playbook
- `GET /api/chat/stream` — Stream chat responses

### Intelligence & Briefing

- `GET /api/intelligence/feed` — Full scored intelligence feed with filters
- `POST /api/intelligence/scrape` — Trigger an immediate scrape
- `GET /api/briefing` — Curated briefing view (top-scored items from last 24h)

### Pipeline Mode (Legacy Sessions)

- `GET /api/sessions` — List pipeline runs
- `POST /api/sessions` — Create a pipeline run
- `GET /api/sessions/{id}` — Get run details
- `POST /api/sessions/{id}/run` — Execute the agent chain

### Settings & Engine Management

- `GET /api/settings/engine` — Tree view of markdown engine (`core/`, `context/`, `skills/`, `playbooks/`, `rubrics/`)
- `PUT /api/settings/engine/file` — Update an engine file (explicit save)
- `GET /api/settings/scraping-config` — Get scraper configuration
- `PUT /api/settings/scraping-config` — Update scraper sources

### File Operations

- `GET /api/files/{path}` — Read a file from the engine
- `PUT /api/files/{path}` — Write a file to the engine (explicit save)

## Database

SQLite database at `forgeos.db` (configurable via `DATABASE_URL` in `.env`). Schema is auto-migrated on startup using SQLModel.

**Key tables:**
- `project` — Top-level content projects
- `folder` — Nested organization under projects
- `deliverable` — Final content output (markdown, status, metadata)
- `brief` — Structured brief (input shape for content generation)
- `chat_session` — Conversation thread
- `chat_message` — Individual messages
- `pipeline_run` — Fire-and-forget agent chain execution (legacy Sessions)
- `scrape_item` — Scored intelligence items from web scraping
- `pipeline_step` — Intermediate outputs per agent in a pipeline run

## Scraping

The system runs a scheduled scraper twice daily (configurable via APScheduler cron). It reads from:

- **Hacker News** (Algolia API) — `hn`
- **GitHub** (topics RSS) — `github`
- **ArXiv** (RSS) — `arxiv`
- **Reddit** (JSON API) — `reddit`
- **Generic RSS feeds** — `rss`

Each scraped item is scored by `services/scoring.py` using a scoring prompt from `context/07_research/intelligence-scoring-prompt.md`. Items with score ≥7 are included in the Briefing Book; all items appear in the Intelligence feed.

**Configure scraping:**
1. Open Settings → Scraping Config
2. Edit sources, keywords, subreddits, RSS feeds
3. Scoring prompt is editable in `context/07_research/intelligence-scoring-prompt.md`
4. Trigger immediate scrape via "Refresh now" button or `/api/intelligence/scrape`

## Testing

Run tests with pytest:

```bash
pytest
```

Tests are in `tests/` (if any exist).

## Instrumentation

ForgeOS dogfoods Arize AX observability. Tracing is wired via `instrumentation.py`:

- Agent runs are traced with `CHAIN` spans
- Claude calls are auto-instrumented via `openinference-instrumentation-anthropic`
- Scraping jobs are traced
- Chat and pipeline endpoints are traced

Traces export to Arize if `ARIZE_SPACE_ID` and `ARIZE_API_KEY` are set. Otherwise, traces are printed to console.

## Architecture

```
apps/api/
├── main.py                  # App entry point, router registration
├── config.py                # Settings (environment variables)
├── models.py                # SQLModel definitions
├── database.py              # SQLite connection
├── cache.py                 # In-memory TTL cache
├── instrumentation.py       # Arize AX tracing setup
├── requirements.txt         # Python dependencies
├── routers/                 # Endpoint handlers
│   ├── projects.py          # /api/projects, /api/folders, /api/deliverables
│   ├── briefing.py          # /api/briefing (curated briefing view)
│   ├── chat.py              # /api/chat/* (interactive mode)
│   ├── intelligence.py      # /api/intelligence/* (full feed + scraping)
│   ├── sessions.py          # /api/sessions/* (legacy pipeline mode)
│   ├── settings.py          # /api/settings/* (engine management)
│   └── files.py             # /api/files/* (markdown engine file I/O)
├── services/                # Business logic
│   ├── file_engine.py       # Markdown engine abstraction
│   ├── generation.py        # Playbook execution & content generation
│   ├── scoring.py           # Intelligence item scoring
│   └── scraping.py          # Web scraper implementations
└── scripts/                 # Utilities
    ├── validate_repo_structure.py
    └── lint_skill_files.py
```

**No Redis, no background workers.** Scheduled jobs (scraping) use APScheduler with in-process persistence. All async I/O uses Python's native `asyncio`.

---

For more context, see the [main README](../../README.md).
