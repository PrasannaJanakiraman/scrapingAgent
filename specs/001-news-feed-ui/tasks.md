# Tasks: News Feed UI

**Input**: Design documents from `/specs/001-news-feed-ui/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks — tests were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the static file directory structure and mount static files in the backend

- [X] T001 Create directory structure: `static/`, `static/css/`, `static/js/`
- [X] T002 Add `StaticFiles` mount to `main.py` — add `app.mount("/static", StaticFiles(directory="static"), name="static")` after the CORS middleware block

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the base HTML page with three-region CSS Grid layout and the core JavaScript module with API client and rendering utilities

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create base HTML document in `static/index.html` — include `<!DOCTYPE html>`, charset, viewport meta, link to `/static/css/styles.css`, script tag for `/static/js/app.js` (defer), and three layout regions: `<nav class="top-bar">` with app name, `<aside class="sidebar">` (empty placeholder), `<main class="feed">` (empty placeholder)
- [X] T004 Create base stylesheet in `static/css/styles.css` — CSS reset/box-sizing, CSS Grid layout on `body` with `grid-template-areas: "nav nav" "sidebar feed"`, `grid-template-columns: 260px 1fr`, `grid-template-rows: 56px 1fr`, full viewport height. Style `.top-bar` fixed at top with background color and app title. Style `.sidebar` with padding and scrollable overflow. Style `.feed` with padding and scrollable overflow.
- [X] T005 Create core JavaScript module in `static/js/app.js` — `"use strict"`, define `API_BASE` constant, implement `async function fetchItems(category, status)` that calls `GET /api/items` with optional query params and returns `{ items: [] }`, implement `async function fetchFilters()` that calls `GET /api/filters` and returns `{ categories: [], statuses: [] }`. Both functions must use try/catch and surface errors to a `showError(message)` function that renders an error banner in `.feed`.

**Checkpoint**: Opening `http://localhost:8000/` should show the three-region layout (top bar, empty sidebar, empty feed area). No data displayed yet.

---

## Phase 3: User Story 1 — Browse Scraped Content Feed (Priority: P1) 🎯 MVP

**Goal**: Display all scraped items as rectangular card boxes with title, 2-line summary, and category > status breadcrumb

**Independent Test**: Open the page → verify items appear as cards, each showing title at top, summary below (max 2 lines), and breadcrumb trail at bottom. If no items exist, verify empty-state message appears.

### Implementation for User Story 1

- [X] T006 [US1] Add card styles to `static/css/styles.css` — `.card` as a rectangular box with border/shadow, padding, margin-bottom. `.card-title` bold at top. `.card-summary` with `display: -webkit-box`, `-webkit-line-clamp: 2`, `overflow: hidden` for 2-line truncation. `.card-breadcrumb` at bottom in smaller muted text showing "Category > Status". Add `.empty-state` style for centered message. Add `.error-banner` style for error messages.
- [X] T007 [US1] Implement `renderCards(items)` function in `static/js/app.js` — takes an array of item objects, clears `.feed` content, and for each item creates a `.card` div containing: `.card-title` with `item.sourceName` (fallback to truncated `item.url` if empty), `.card-summary` with `item.summary` (fallback to "No summary available"), `.card-breadcrumb` with `item.category + " > " + item.status`. If items array is empty, render `.empty-state` with "No items available."
- [X] T008 [US1] Implement `init()` function in `static/js/app.js` — on `DOMContentLoaded`, call `fetchItems()` with no filters, pass result to `renderCards()`. Handle fetch errors by calling `showError("Unable to connect to the server. Please try again later.")`

**Checkpoint**: Opening `http://localhost:8000/` shows all scraped items as cards. Empty database shows "No items available." Unreachable backend shows error message.

---

## Phase 4: User Story 2 — Filter Content by Category (Priority: P2)

**Goal**: Add a Category dropdown to the sidebar that filters the feed when a value is selected

**Independent Test**: Select a category from the dropdown → only matching items appear. Select "All" → full feed restored.

### Implementation for User Story 2

- [X] T009 [US2] Add sidebar filter styles to `static/css/styles.css` — `.filter-group` with label and select styling, `.filter-group label` bold, `.filter-group select` full-width with padding
- [X] T010 [US2] Add Category dropdown markup to `static/index.html` — inside `<aside class="sidebar">`, add a `<div class="filter-group">` with `<label for="category-filter">Category</label>` and `<select id="category-filter"><option value="">All</option></select>`
- [X] T011 [US2] Implement `populateFilters()` in `static/js/app.js` — call `fetchFilters()`, populate `#category-filter` select with an `<option>` for each category value (keeping "All" as first option with empty value)
- [X] T012 [US2] Add category filter event listener in `static/js/app.js` — on `#category-filter` change, read selected value, call `fetchItems(category, currentStatus)` with the selected category (null if "All"), pass result to `renderCards()`. Store selected category in a module-level `selectedCategory` variable. Update `init()` to call `populateFilters()`.

**Checkpoint**: Category dropdown populated on load. Selecting a category filters the feed. Selecting "All" restores full feed.

---

## Phase 5: User Story 3 — Filter Content by Status (Priority: P2)

**Goal**: Add a State dropdown to the sidebar that filters the feed by status, combinable with Category filter

**Independent Test**: Select a status → only matching items appear. Combine with category filter → both filters applied. Clear both → full feed restored.

### Implementation for User Story 3

- [X] T013 [US3] Add State dropdown markup to `static/index.html` — inside `<aside class="sidebar">`, add a second `<div class="filter-group">` with `<label for="status-filter">State</label>` and `<select id="status-filter"><option value="">All</option></select>`
- [X] T014 [US3] Extend `populateFilters()` in `static/js/app.js` — also populate `#status-filter` select with status values from the filters API response
- [X] T015 [US3] Add status filter event listener in `static/js/app.js` — on `#status-filter` change, read selected value, call `fetchItems(selectedCategory, status)` with both current filters. Store selected status in a module-level `selectedStatus` variable.
- [X] T016 [US3] Add "Clear Filters" button — add a `<button id="clear-filters" class="clear-filters-btn">Clear Filters</button>` below the filter groups in the sidebar. On click, reset both dropdowns to "All", clear `selectedCategory` and `selectedStatus`, and re-fetch all items. Add `.clear-filters-btn` styles to `static/css/styles.css`. Update empty-state message to "No items match your filters" when filters are active vs "No items available" when no filters.

**Checkpoint**: Both filters work independently and together. "Clear Filters" resets everything. Empty filter results show contextual message.

---

## Phase 6: User Story 4 — Navigate with Top Bar (Priority: P3)

**Goal**: Ensure the top navigation bar is fixed, shows the application name, and remains visible during scrolling

**Independent Test**: Scroll down through a long feed → top bar stays visible and fixed at the top of the viewport.

### Implementation for User Story 4

- [X] T017 [US4] Finalize top bar styles in `static/css/styles.css` — ensure `.top-bar` has `position: sticky`, `top: 0`, `z-index: 100`, appropriate background color, and the application name/logo text is styled prominently. Verify the grid layout keeps the nav bar fixed while sidebar and feed scroll independently.

**Checkpoint**: Top bar remains fixed when scrolling the feed. Application name is clearly visible.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T018 [P] Add responsive guard in `static/css/styles.css` — add a `@media (max-width: 1023px)` rule that displays a message indicating the app requires a 1024px+ viewport (per spec assumption)
- [X] T019 [P] Add loading indicator in `static/js/app.js` — show a "Loading..." message in `.feed` while API calls are in flight, using the `isLoading` state from the data model
- [X] T020 Run quickstart.md validation scenarios VS-001 through VS-008 manually in browser

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion
  - US1 (Phase 3) must complete before US2/US3 (they extend its rendering logic)
  - US2 and US3 can proceed sequentially or in parallel after US1
  - US4 (Phase 6) is independent of US2/US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (needs `renderCards()` and `fetchItems()` from US1)
- **User Story 3 (P2)**: Depends on US2 (extends filter infrastructure from US2)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) — Independent of US1/US2/US3

### Within Each User Story

- CSS before JS (styles must exist for rendered elements)
- HTML structure before JS logic (DOM elements must exist for selectors)
- Core rendering before event handling

### Parallel Opportunities

- T001 and T002 in Setup are sequential (directory must exist before mount)
- T003, T004, T005 in Foundational can run in parallel (different files)
- T017 (US4) can run in parallel with US2/US3 after US1 completes
- T018 and T019 in Polish can run in parallel (different files)

---

## Parallel Example: Foundational Phase

```text
# These three tasks create different files and can run in parallel:
Task T003: "Create base HTML document in static/index.html"
Task T004: "Create base stylesheet in static/css/styles.css"
Task T005: "Create core JavaScript module in static/js/app.js"
```

## Parallel Example: After User Story 1

```text
# US4 is independent and can run alongside US2:
Task T017: "Finalize top bar styles in static/css/styles.css"  (US4)
Task T009: "Add sidebar filter styles in static/css/styles.css" (US2)
# Note: T009 and T017 both touch styles.css — run sequentially or coordinate sections
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T005)
3. Complete Phase 3: User Story 1 (T006–T008)
4. **STOP and VALIDATE**: Open browser, verify cards display with title/summary/breadcrumb
5. Deploy/demo if ready — core value delivered

### Incremental Delivery

1. Setup + Foundational → Three-region layout visible
2. Add User Story 1 → Cards display → Deploy/Demo (MVP!)
3. Add User Story 2 → Category filter works → Deploy/Demo
4. Add User Story 3 → Status filter + combined filters → Deploy/Demo
5. Add User Story 4 → Fixed nav bar polished → Deploy/Demo
6. Polish → Loading states, viewport guard, full validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All three frontend files (`index.html`, `styles.css`, `app.js`) are in `static/`
- Only `main.py` needs a one-line backend change (T002)
