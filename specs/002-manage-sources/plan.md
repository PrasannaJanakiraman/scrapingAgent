# Implementation Plan: Manage Sources

**Branch**: `002-manage-sources` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-manage-sources/spec.md`

## Summary

Add a "Manage Sources" button to the top-right of the existing navigation
bar. Clicking it opens a modal overlay containing a file upload control
(for .xlsx files) and a data table showing all scraped sources. Uploading
a file triggers the existing `POST /scrape` endpoint, shows progress,
and refreshes the table on completion. The feature extends the existing
News Feed UI (feature 001) using plain HTML, CSS, and JavaScript.

## Technical Context

**Language/Version**: JavaScript (ES6+), HTML5, CSS3

**Primary Dependencies**: None (vanilla JS). Backend: FastAPI with
existing `POST /scrape` and `GET /api/items` endpoints

**Storage**: N/A (all data fetched from backend CosmosDB via API)

**Testing**: Manual browser testing against acceptance scenarios

**Target Platform**: Desktop browsers (Chrome, Firefox, Edge, Safari),
viewport 1024px+

**Project Type**: Static web frontend extending existing FastAPI-served UI

**Performance Goals**: Table load < 2s; scrape feedback within 5s of
completion

**Constraints**: Zero external JS libraries; no build tools; extends
existing `static/` files from feature 001

**Scale/Scope**: Single modal overlay, ~2 user stories, table of
hundreds of rows (no pagination required)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | PASS | Extends existing HTML/CSS/JS files, no new dependencies. Modal is vanilla JS. |
| II. Backend Integration | PASS | Uses existing `POST /scrape` and `GET /api/items` endpoints. Error handling for all API calls. |
| III. User Experience | PASS | Table loads in < 2s. Progress indicator during scrape. Empty/error states defined. |
| IV. Code Quality | PASS | Strict mode, single-responsibility functions, kebab-case CSS. |
| V. Progressive Delivery | PASS | US1 (upload/scrape) before US2 (table view). Each independently testable. |

No violations. Complexity Tracking section not needed.

## Project Structure

### Documentation (this feature)

```text
specs/002-manage-sources/
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
├── index.html           # Extended: add Manage Sources button + modal markup
├── css/
│   └── styles.css       # Extended: add modal, table, upload, and button styles
└── js/
    └── app.js           # Extended: add modal logic, file upload, table rendering
```

**Structure Decision**: Extends the existing `static/` files from
feature 001. No new files needed — the modal, upload form, and table
are added to the existing three files. This follows Constitution
Principle I (Simplicity First) and avoids file proliferation.

## Complexity Tracking

> No violations detected. This section is intentionally empty.
