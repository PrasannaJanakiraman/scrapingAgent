# Implementation Plan: News Feed UI

**Branch**: `001-news-feed-ui` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-news-feed-ui/spec.md`

## Summary

Build a lightweight frontend using plain HTML, CSS, and JavaScript that
displays scraped regulatory content from the existing FastAPI backend
as a filterable news feed. The UI has three regions: a fixed top
navigation bar, a left sidebar with Category and State filters, and
a right-side scrollable card feed. Static files are served by FastAPI
from a `static/` directory.

## Technical Context

**Language/Version**: JavaScript (ES6+), HTML5, CSS3

**Primary Dependencies**: None (vanilla JS). Backend: FastAPI 0.136.3

**Storage**: N/A (all data fetched from backend CosmosDB via API)

**Testing**: Manual browser testing against acceptance scenarios

**Target Platform**: Desktop browsers (Chrome, Firefox, Edge, Safari),
viewport 1024px+

**Project Type**: Static web frontend served by existing FastAPI backend

**Performance Goals**: Page load to visible content < 3s; filter
response < 2s

**Constraints**: Zero external JS libraries; no build tools or
transpilers; static files only

**Scale/Scope**: Single page, ~4 user stories, hundreds of items
(no pagination required)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | Plain HTML/CSS/JS, zero dependencies, no build tools |
| II. Backend Integration | PASS | All data from `/api/items` and `/api/filters`; error states defined |
| III. User Experience | PASS | Performance targets match spec SC-001/SC-002; three-region layout per SC-003 |
| IV. Code Quality | PASS | Strict mode, single-responsibility functions, BEM/kebab-case CSS planned |
| V. Progressive Delivery | PASS | Stories ordered P1→P2→P3; each independently testable |

No violations. Complexity Tracking section not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-news-feed-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-contracts.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
static/
├── index.html           # Single-page HTML with layout structure
├── css/
│   └── styles.css       # All styles (layout, cards, filters, nav)
└── js/
    └── app.js           # API calls, filtering logic, DOM rendering
```

**Structure Decision**: Single-project flat structure under `static/`.
This is a static frontend with three files — no `src/`, `components/`,
or build pipeline needed. The `static/` directory is served directly
by FastAPI's existing static file configuration. This is the simplest
structure that satisfies all requirements.

## Complexity Tracking

> No violations detected. This section is intentionally empty.
