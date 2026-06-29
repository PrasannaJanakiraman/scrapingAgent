# Tasks: Manage Sources

**Input**: Design documents from `/specs/002-manage-sources/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks — tests were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new files or directories needed — this feature extends existing `static/` files from feature 001.

- [X] T001 Verify existing files are in place: `static/index.html`, `static/css/styles.css`, `static/js/app.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add modal overlay infrastructure and "Manage Sources" button to the nav bar. These are shared by both user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add "Manage Sources" button markup to `static/index.html` — inside `<nav class="top-bar">`, add a `<button id="manage-sources-btn" class="manage-sources-btn">Manage Sources</button>` on the right side of the nav bar (use flexbox spacer or `margin-left: auto`)
- [X] T003 Add modal overlay markup to `static/index.html` — add a `<div id="manage-sources-modal" class="modal-overlay hidden">` containing: a `<div class="modal-content">` with a `<div class="modal-header">` (title "Manage Sources" + close button `<button class="modal-close">&times;</button>`), a `<div class="modal-body">` (empty placeholder for upload form and table)
- [X] T004 Add modal and button styles to `static/css/styles.css` — `.manage-sources-btn` styled as a nav bar button (right-aligned, white text, border). `.modal-overlay` as fixed full-screen with semi-transparent black backdrop, centered flexbox, z-index 200. `.modal-content` white background, rounded corners, max-width 800px, max-height 80vh, overflow-y auto. `.modal-header` with flex layout (title left, close button right). `.modal-close` styled as borderless button. `.hidden` class with `display: none`.
- [X] T005 Add modal open/close logic to `static/js/app.js` — `openModal()` removes `.hidden` from `#manage-sources-modal`, `closeModal()` adds `.hidden`. Click handler on `#manage-sources-btn` calls `openModal()`. Click handler on `.modal-close` calls `closeModal()`. Click handler on `.modal-overlay` calls `closeModal()` if clicking backdrop (not `.modal-content`).

**Checkpoint**: "Manage Sources" button visible in top-right of nav bar. Clicking it opens an empty modal overlay. Clicking X or backdrop closes it.

---

## Phase 3: User Story 1 — Upload Excel Configuration File (Priority: P1) 🎯 MVP

**Goal**: Add file upload control to the modal that triggers the backend scrape endpoint with progress indication and success/error feedback

**Independent Test**: Click "Manage Sources" → select a .xlsx file → verify scrape triggers with progress indicator → verify success/error message appears.

### Implementation for User Story 1

- [X] T006 [US1] Add upload form markup to `static/index.html` — inside `.modal-body`, add a `<div class="upload-section">` containing: `<label for="scrape-file-input" class="upload-label">Upload Excel Configuration</label>`, `<input type="file" id="scrape-file-input" accept=".xlsx">`, `<button id="upload-btn" class="upload-btn">Upload & Scrape</button>`, `<div id="upload-status" class="upload-status"></div>` for progress/success/error messages
- [X] T007 [US1] Add upload form styles to `static/css/styles.css` — `.upload-section` with padding and margin-bottom. `.upload-label` bold. `.upload-btn` styled as primary action button (background color matching nav bar, white text, padding, border-radius, full-width or auto). `.upload-btn:disabled` with reduced opacity and cursor not-allowed. `.upload-status` for message display. `.upload-status.success` green text. `.upload-status.error` red text. `.upload-status.loading` with italic style.
- [X] T008 [US1] Implement file upload logic in `static/js/app.js` — add module-level `let isUploading = false`. Implement `async function uploadFile()`: validate that a file is selected and has `.xlsx` extension, set `isUploading = true`, disable `#upload-btn`, show "Scraping in progress..." in `#upload-status` with `.loading` class, create `FormData` with the file, `POST` to `/scrape` via `fetch()`, on success show "Scrape completed successfully!" with `.success` class and call `loadSourceTable()`, on error show error detail from response with `.error` class, finally set `isUploading = false` and re-enable `#upload-btn`. Add click handler on `#upload-btn` that calls `uploadFile()` if not already uploading.
- [X] T009 [US1] Update `openModal()` in `static/js/app.js` — when modal opens, clear the file input value and clear `#upload-status` text

**Checkpoint**: Upload a .xlsx file → spinner/progress message shows → success message appears on completion. Upload invalid file → error message. Button disabled during scrape.

---

## Phase 4: User Story 2 — View Source Data Table (Priority: P2)

**Goal**: Display a table of all scraped source records with Source ID, Source Name, Status, and Scrape Date columns

**Independent Test**: Open Manage Sources modal → table displays all scraped records. If no data exists, "No sources have been added yet" message appears. After successful scrape, table refreshes with new data.

### Implementation for User Story 2

- [X] T010 [US2] Add table markup to `static/index.html` — inside `.modal-body`, below `.upload-section`, add a `<div class="source-table-section">` containing: `<h3>Scraped Sources</h3>` and `<div id="source-table-container"></div>` (table will be rendered via JS)
- [X] T011 [US2] Add table styles to `static/css/styles.css` — `.source-table-section` with padding-top and border-top separator. `.source-table` full-width, border-collapse, text-align left. `.source-table th` with background color, padding, font-weight bold, border-bottom. `.source-table td` with padding, border-bottom. `.source-table tr:hover` with light background highlight. `.source-table-empty` centered muted text for empty state.
- [X] T012 [US2] Implement `loadSourceTable()` in `static/js/app.js` — call `fetchItems()` with no filters (reuse existing function), render a `<table class="source-table">` into `#source-table-container` with `<thead>` containing columns: Source ID, Source Name, Status, Scrape Date. For each item, create a `<tr>` with `<td>` for `item.sourceId`, `item.sourceName` (fallback "Unknown"), `item.status`, and `new Date(item.scrapeDate).toLocaleString()`. If no items, render `<div class="source-table-empty">No sources have been added yet.</div>`.
- [X] T013 [US2] Update `openModal()` in `static/js/app.js` — call `loadSourceTable()` when modal opens so table is populated with current data

**Checkpoint**: Open modal → table shows all scraped sources. Empty database → "No sources have been added yet." After successful upload, table refreshes automatically.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T014 [P] Add keyboard support in `static/js/app.js` — close modal on Escape key press
- [X] T015 Run quickstart.md validation scenarios VS-001 through VS-010 manually in browser

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verification only
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–4)**: All depend on Foundational phase completion
  - US1 (Phase 3) must complete before US2 (table refresh depends on `loadSourceTable()` being called from `uploadFile()`)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (US1 calls `loadSourceTable()` on scrape success for automatic refresh)

### Within Each User Story

- HTML markup before CSS styling before JS logic
- Core functionality before refinements

### Parallel Opportunities

- T002, T003 can run sequentially (both modify index.html)
- T004 can run in parallel with T002/T003 (different file: styles.css)
- T006, T007 are sequential within US1 (HTML before CSS)
- T010, T011 are sequential within US2 (HTML before CSS)
- T014 is independent and can run in parallel with T015

---

## Parallel Example: Foundational Phase

```text
# T004 creates styles while T002/T003 add HTML:
Task T002: "Add Manage Sources button to static/index.html"
Task T003: "Add modal overlay markup to static/index.html"
Task T004: "Add modal and button styles to static/css/styles.css"  (parallel with T002/T003)
# Note: T002 and T003 both modify index.html — run sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002–T005)
3. Complete Phase 3: User Story 1 (T006–T009)
4. **STOP and VALIDATE**: Upload a .xlsx file, verify scrape triggers and feedback works
5. Deploy/demo if ready — core upload functionality delivered

### Incremental Delivery

1. Setup + Foundational → Modal opens/closes with button in nav bar
2. Add User Story 1 → File upload and scrape works → Deploy/Demo (MVP!)
3. Add User Story 2 → Source data table visible → Deploy/Demo
4. Polish → Keyboard support, full validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This feature extends existing files from feature 001 (News Feed UI)
- No new source files are created — all changes are additions to `index.html`, `styles.css`, and `app.js`
- The `POST /scrape` endpoint may take significant time — the UI must handle long-running requests gracefully
