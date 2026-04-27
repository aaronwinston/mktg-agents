# ForgeOS Web

Next.js 14 frontend for ForgeOS. Provides the dashboard, workspace, and settings UI.

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd apps/web
npm install
```

## Running

```bash
npm run dev
```

Open `http://localhost:3000`. The app loads instantly and fetches data from the local API.

## Building

```bash
npm run build
npm start
```

> **Note:** Static export is not supported due to dynamic routes in the workspace (`/workspace/[deliverableId]`). The app requires a Node.js server or a serverless platform that supports dynamic routing (Vercel, Next.js Middleware, etc.).

## Linting

```bash
npm run lint
```

Uses `next lint` (ESLint configured for Next.js).

## Architecture

### Pages

- `/` — Dashboard (daily briefing, quote, status)
- `/workspace/[deliverableId]` — Primary UI: three-pane workspace for chat, editing, and briefing
- `/projects` — Project/folder/deliverable tree
- `/settings` — Engine configuration (core/, context/, skills/, playbooks/, rubrics/)

### Key Components

**Layout:**
- `WorkspaceLayout` — Three-pane container (left sidebar, center tabs, right toggles panel)
- `Sidebar` — Project tree with keyboard navigation and search

**Workspace Surfaces:**
- `ChatInterface` — Streaming chat with Claude, message history, markdown rendering
- `EditorTab` — WYSIWYG markdown editor (TipTap) with explicit save
- `BriefTab` — Editable brief view with structured fields

**Right Rail:**
- `TogglesPanel` — Brief-first toggle, audience field, voice selector, skills multi-select, playbook selector, content type
- `ContextInUsePanel` — Shows which context layers, skills, and intelligence items are composed into the current prompt

**Intelligence & Briefing:**
- `BriefingBook` — Curated feed from `/api/briefing` (top-scored items)
- `IntelligenceFeed` — Full scored feed from `/api/intelligence/feed` with filters

**Settings:**
- `EngineEditor` — Tree view of markdown engine with side-by-side editor
- `ScrapingConfig` — Configure sources, keywords, subreddits, RSS feeds
- `IntegrationStubs` — Calendar, reminders, Slack, Gmail, HubSpot (v2, coming soon)

### Data Fetching

Uses React Query (`@tanstack/react-query`) for all API calls. A typed API client in `lib/api.ts` mirrors the backend surface.

**Key hooks:**
- `useProjects()` — Fetch projects/folders/deliverables
- `useBriefs()` — Fetch briefs
- `useDeliverables()` — Fetch deliverables
- `useChatMessages()` — Fetch chat history for a session
- `usePipelineRuns()` — Fetch pipeline run history
- `useEngineTree()` — Fetch markdown engine file tree

### TypeScript

All components and hooks are fully typed. No `any` types without a comment explaining why.

### Styling

Tailwind CSS with a custom design system. Responsive layout (mobile-first) with dark mode support.

**Key design patterns:**
- Loading state: skeleton screens or spinner overlay
- Empty state: friendly message with call-to-action
- Error state: diagnostic message with retry button
- Toast notifications: success, error, info (via `sonner` or similar)

### Keyboard Shortcuts

- `Cmd+Enter` — Send chat message
- `Cmd+S` — Save (in editor or brief)
- Arrow keys — Navigate project tree
- `Escape` — Close modals, deselect items

## Instrumentation

Frontend errors and slow API calls are logged to the browser console. Optionally, integrate with a client-side observability platform (Sentry, LogRocket, etc.) for production.

---

For more context, see the [main README](../../README.md).
