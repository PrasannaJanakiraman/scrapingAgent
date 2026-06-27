# Quickstart: News Feed UI

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Prerequisites

- Python 3.11+ with the backend dependencies installed
  (`pip install -r requirements.txt`)
- The FastAPI backend (`main.py`) must be runnable
- CosmosDB must be accessible with scraped data present
- A modern desktop browser (Chrome, Firefox, Edge, or Safari)

## Setup

1. Ensure the `static/` directory exists at the backend root
   with the frontend files:

   ```text
   static/
   ├── index.html
   ├── css/
   │   └── styles.css
   └── js/
       └── app.js
   ```

2. Ensure the backend `main.py` has the `StaticFiles` mount:

   ```python
   from fastapi.staticfiles import StaticFiles
   app.mount("/static", StaticFiles(directory="static"), name="static")
   ```

   This line must appear after the `app` instance is created and
   before `uvicorn.run()`.

## Running

Start the backend server:

```bash
cd c:\prasanna\TrainingPlan\ScrapingAgent\APP_SERVICE\reactapp
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open a browser and navigate to `http://localhost:8000/`.

## Validation Scenarios

### VS-001: Page loads with content (SC-001, FR-003, FR-005)

1. Open `http://localhost:8000/`
2. **Expected**: The page displays within 3 seconds. A top navigation
   bar is visible. The left sidebar shows Category and State dropdowns.
   The right side shows scraped items as rectangular card boxes.
3. **Verify**: Each card shows a title at the top, a 2-line summary
   below, and a breadcrumb trail (Category > State) at the bottom.

### VS-002: Category filter works (SC-002, FR-006)

1. From the loaded page, select a category from the sidebar dropdown.
2. **Expected**: Within 2 seconds, only items matching the selected
   category appear in the feed. No full page reload occurs.
3. Clear the category filter.
4. **Expected**: All items reappear.

### VS-003: State filter works (SC-002, FR-007)

1. Select a status from the State dropdown.
2. **Expected**: Only items with that status appear.
3. Clear the filter.
4. **Expected**: All items reappear.

### VS-004: Combined filters (FR-008)

1. Select both a category and a status.
2. **Expected**: Only items matching both filters appear.
3. Clear all filters (FR-009).
4. **Expected**: Full unfiltered feed is restored.

### VS-005: Empty state (FR-011)

1. Select a filter combination that returns zero results.
2. **Expected**: A message like "No items match your filters" appears
   in the content area instead of a blank space.

### VS-006: Error handling (FR-012)

1. Stop the backend server.
2. Refresh the page (or trigger a filter change).
3. **Expected**: A user-friendly error message appears (e.g.,
   "Unable to connect to the server. Please try again later.").

### VS-007: Layout structure (SC-003)

1. Open the page on a 1024px-wide viewport.
2. **Expected**: Three regions visible — fixed top nav bar, left
   sidebar, right content area. All regions properly sized and
   non-overlapping.

### VS-008: Navigation bar persistence (FR-001)

1. Scroll down through a long feed.
2. **Expected**: The top navigation bar remains fixed and visible.
