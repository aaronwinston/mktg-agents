# ForgeOS

**An AI-native editorial and marketing operating system.**

Most AI writing tools give you a chat box. ForgeOS gives you an editorial team — a sequenced chain of specialized agents that take a brief and run it through research, drafting, review, fact-checking, SEO, legal risk, and distribution planning before handing you a finished document.

It runs locally. It costs nothing beyond your Anthropic API key. And the whole thing is built on a markdown knowledge base you own and control.

---

## Why this exists

Marketing teams that build with AI usually hit the same wall: the output is fast but generic. It doesn't sound like you. It doesn't know your voice, your audience, your claims policy, or your brand standards. You spend as much time editing as you would have spent writing.

ForgeOS is built around a different premise. Before any agent writes a word, it reads your voice guide, your style standards, your messaging framework, your claims policy, and your editorial principles. The context isn't bolted on — it's the foundation.

The result is content that actually sounds like you came out of it. Faster, but not at the cost of quality or brand consistency.

---

## What it does

**Two layers work together:**

### 1. The Engine (the markdown brain)

A structured knowledge base at the repo root. These files are the source of truth for everything the agents know about your brand, voice, and standards:

| Directory | What lives here |
|-----------|-----------------|
| `core/` | Voice guide, style guide, claims policy, brand standards, editorial principles |
| `context/` | 8-layer context system — philosophy through research |
| `skills/` | 19 specialist agent definitions (researcher, copywriter, SEO, legal, and more) |
| `playbooks/` | Sequenced production workflows for each content type |
| `rubrics/` | Quality scoring rubrics used during review |
| `briefs/` | Intake brief templates for every content type |
| `prompts/` | Reusable prompt templates |
| `examples/` | Reference outputs at different quality tiers |

You edit these files. Agents read them. The system improves as the knowledge base improves.

### 2. The Cockpit (the web app)

A local Next.js dashboard that wraps the engine with a UI:

- **Dashboard** — daily briefing feed powered by Claude (pulls from Hacker News, GitHub Trending, and ArXiv), active session status, and a daily rotating quote
- **Sessions** — create content sessions, run the 11-agent chain, watch agents work in real time, and edit the final output
- **Agent Tracker** — a persistent right panel showing which agent is active, what it's doing, and where you are in the chain
- **Chat** — context-aware streaming chat with the full system prompt loaded
- **Intelligence** — scraped and scored items from the web, ready to use as source material
- **Projects** — organize sessions into projects

---

## The agent chain

Every content session runs through 11 specialist agents in sequence. Each one reads the accumulated output from the previous agent, applies its skill set, and passes an improved draft forward.

```
editorial-director    →  Sets strategy, frames the narrative
ai-researcher         →  Gathers sources, validates claims
dev-copywriter        →  Writes the draft
dev-reviewer          →  Tightens copy, improves structure
technical-fact-checker →  Verifies technical accuracy
seo-strategist        →  Optimizes for search without sacrificing voice
copy-chief            →  Final editorial pass
claims-risk-reviewer  →  Flags unsupported or risky claims
final-publish-reviewer →  Publish readiness check
social-editor         →  Derives social content from the piece
content-ops-manager   →  Distribution and repurposing plan
```

Each agent loads its own `SKILL.md` file before running, so its behavior is fully inspectable and editable. Change the skill file, change the agent.

---

## Getting started

### Prerequisites

- Python 3.9+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone the repo

```bash
git clone https://github.com/aaronwinston/forgeos.git
cd forgeos
```

### 2. Start the backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Then run:
```bash
python -m uvicorn main:app --reload --port 8000
```

On first run, seed the demo sessions:
```bash
python scripts/seed_demo.py
```

The API will be live at `http://localhost:8000`. Check `http://localhost:8000/api/health` to confirm.

### 3. Start the frontend

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`. The dashboard loads instantly — quote, layout, and nav are all static. The briefing feed and session data come from the local API.

> **If the API isn't running**, the app shows a friendly message with the command to start it. Nothing breaks. Nothing red.

---

## How to use it

### Run a content session

1. Click **+ New Session** on the dashboard or the Sessions page
2. Give it a title, type (blog, email, social, launch), audience, and a description or brief
3. Open the session and click **Run Chain**
4. Watch the agents work in the Agent Tracker on the right
5. When the chain completes, the final document is in the editor — copy it, edit it, ship it

### Refresh the briefing feed

Click **Refresh briefing ↻** on the dashboard. The backend pulls top stories from Hacker News, GitHub Trending, and ArXiv, sends them to Claude for editorial filtering, and returns the 8 most relevant stories for your team — each with a content angle attached.

Results are cached for 30 minutes so you're not burning API calls on every page load.

### Edit the knowledge base

The markdown files at the repo root are the system's brain. Edit them directly:

- Change your voice? Update `core/VOICE.md`
- Add a new agent skill? Drop a `SKILL.md` in `skills/{category}/{agent-name}/`
- Refine a workflow? Edit the relevant file in `playbooks/`

Every agent reads these files before running. The system gets better as the knowledge base gets better.

### Validate the repo structure

```bash
cd apps/api
source venv/bin/activate
python scripts/validate_repo_structure.py
python scripts/lint_skill_files.py
```

---

## Architecture

```
forgeos/
├── core/                        # Voice, style, claims, brand standards
├── context/                     # 8-layer context system
│   ├── 00_orchestration/        # Context routing instructions
│   ├── 01_philosophy/           # Developer marketing principles
│   ├── 02_narrative/            # Messaging frameworks
│   ├── 03_strategy/             # Content strategy
│   ├── 04_execution/            # Campaign blueprints
│   ├── 05_patterns/             # Proven content patterns
│   ├── 06_influence/            # Analyst relations
│   └── 07_research/             # Market research playbooks
├── skills/                      # Agent skill definitions (19 agents)
│   ├── editorial/               # editorial-director, copy-chief, content-ops-manager
│   ├── foundation/              # ai-researcher, dev-copywriter, dev-reviewer
│   ├── specialization/          # seo-strategist, social-editor, technical-fact-checker, and more
│   └── quality/                 # claims-risk-reviewer, final-publish-reviewer
├── playbooks/                   # Sequenced production workflows
├── rubrics/                     # Quality scoring rubrics
├── briefs/                      # Intake brief templates
├── prompts/                     # Reusable prompt templates
├── examples/                    # Reference quality tiers
└── apps/
    ├── api/                     # FastAPI backend
    │   ├── main.py              # App entry point, router registration
    │   ├── runner.py            # 11-agent chain executor
    │   ├── cache.py             # In-memory TTL cache (no Redis)
    │   ├── database.py          # SQLite via SQLModel
    │   ├── models.py            # AgentSession, Project, ChatSession, and more
    │   └── routers/             # sessions, briefing, chat, projects, files, intelligence
    └── web/                     # Next.js 14 frontend
        └── src/
            ├── app/             # Pages: dashboard, sessions, projects, settings
            ├── components/      # UI, layout, dashboard, sessions components
            └── lib/             # API client, quote utility
```

**No cloud database. No auth service. No Redis. No Vercel.** SQLite on disk. Static frontend. One API key.

---

## What's next

ForgeOS is early. The foundation is solid — the markdown engine, the agent chain, the briefing feed, the session workspace. But there's a lot of ground left to cover.

**Near-term**
- `output: 'export'` static site mode so the frontend deploys to GitHub Pages without a Node server (blocked by dynamic session routes — needs a routing fix)
- Multi-agent parallelism for research tasks
- Brief generation UI — fill out a form, get a structured brief, run the chain
- Agent output streaming directly into the document editor (live updates vs. waiting for completion)

**Medium-term**
- Calendar and pipeline view — see what's scheduled, what's in flight, what's done
- Slack integration — push finished content to channels, get briefings via DM
- Twitter/X scraper — the interface exists, the implementation is stubbed
- Broad web search integration — search as a research step inside agent runs
- Rubric-based quality scoring — auto-score drafts against editorial rubrics before surfacing

**Longer-term**
- Multi-user support with role-based access
- Gmail and HubSpot integrations for distribution tracking
- Custom agent builder — define new agents in the UI without touching markdown
- Eval harness — run sample briefs against expected outputs, measure quality drift over time

---

## Looking for contributors

This project is open source and actively evolving. I'm one person building this between other work, and there's more to do than I can do alone.

If any of this sounds interesting to work on, I'd love to hear from you:

- **Frontend engineers** — the UI is functional but there's a lot of room to make it excellent
- **Python developers** — the agent runner, scraping pipeline, and API all have meaningful improvements on the roadmap
- **AI/ML engineers** — evals, scoring, parallelism, and smarter context loading are all open problems
- **Technical writers** — the knowledge base is the product; good writers who understand AI tooling are as valuable as engineers here
- **Marketers who code** — this tool is built for people like you, and your feedback shapes the roadmap

Open an issue, start a discussion, or reach out directly. The best contributions usually start with a conversation.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.9+ |
| Database | SQLite (via SQLModel) |
| LLM | Anthropic Claude (claude-sonnet-4-5) |
| Frontend | Next.js 14 + TypeScript |
| Styling | Tailwind CSS |
| Data fetching | SWR |
| Observability | Arize AX (OpenTelemetry) |

---

## License

MIT. Use it, fork it, build on it.
