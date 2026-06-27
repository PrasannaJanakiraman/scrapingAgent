# Research: News Feed UI

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Research Summary

All technical context items have been resolved. The existing FastAPI
backend (at `reactapp/main.py`) already provides the two API endpoints
needed (`/api/items` and `/api/filters`) plus CORS middleware and a
root route for serving `index.html`. No NEEDS CLARIFICATION items
remain.

## Decision Log

### D-001: Frontend Technology

- **Decision**: Plain HTML5, CSS3, JavaScript (ES6+) with no frameworks
  or libraries.
- **Rationale**: Constitution Principle I (Simplicity First) mandates
  no frameworks. The UI has a single page with two API calls and basic
  DOM manipulation — a framework would add unnecessary complexity.
- **Alternatives considered**: React, Vue, Svelte — all rejected per
  constitution and spec FR-013.

### D-002: Static File Serving

- **Decision**: Place all frontend files in `static/` directory at the
  backend root. FastAPI serves `index.html` via the existing `GET /`
  route.
- **Rationale**: The backend already has a `STATIC_DIR` constant
  pointing to `{backend_root}/static/` and a root route returning
  `FileResponse(STATIC_DIR / "index.html")`. No backend changes needed.
- **Alternatives considered**: Separate dev server with proxy — rejected
  as it adds infrastructure complexity. Inline HTML in backend
  templates — rejected as it couples frontend to Python code.
- **Note**: The backend currently only serves `index.html` at `/`. CSS
  and JS files will need a `StaticFiles` mount added (e.g.,
  `app.mount("/static", StaticFiles(directory="static"))`) or the HTML
  must reference assets via relative paths that the existing route can
  serve. This is a minor backend change.

### D-003: API Integration Pattern

- **Decision**: Use the Fetch API with async/await for all backend
  calls. No XMLHttpRequest or third-party HTTP libraries.
- **Rationale**: Fetch is natively available in all target browsers
  (Chrome, Firefox, Edge, Safari modern versions). Async/await
  produces readable, linear code.
- **Alternatives considered**: XMLHttpRequest — rejected as verbose
  and callback-based. Axios — rejected per zero-dependency constraint.

### D-004: Filtering Strategy

- **Decision**: Client-side filtering by re-fetching from the backend
  with query parameters (`?category=X&status=Y`).
- **Rationale**: The backend `/api/items` endpoint already accepts
  optional `category` and `status` query parameters and returns
  filtered results. Server-side filtering is more accurate and
  avoids loading all items into memory on the client.
- **Alternatives considered**: Client-side filtering (fetch all, filter
  in JS) — viable for small datasets but less scalable and duplicates
  backend logic.

### D-005: CSS Architecture

- **Decision**: Single `styles.css` file using kebab-case class names
  with a flat structure. CSS Grid for the three-region layout, Flexbox
  for card internals.
- **Rationale**: Constitution Principle I favors a single stylesheet.
  CSS Grid provides the cleanest way to define the three-region layout
  (nav bar, sidebar, main content). The project scope is small enough
  that BEM namespacing is unnecessary.
- **Alternatives considered**: BEM — rejected as over-engineering for
  a single-page app with ~20 classes. CSS-in-JS — rejected per
  no-framework constraint.

### D-006: Error Handling

- **Decision**: Display a user-friendly error banner in the main
  content area when API calls fail. Use `try/catch` around all
  fetch calls.
- **Rationale**: Spec FR-012 requires user-friendly error messages
  when backend is unreachable. Constitution Principle II requires
  all API calls to include error handling.
- **Alternatives considered**: Toast notifications — rejected as
  they require additional UI complexity. Silent failures — rejected
  as they violate spec requirements.

### D-007: Empty State Handling

- **Decision**: Show a centered message in the main content area
  with contextual text ("No items found" vs "No items match your
  filters").
- **Rationale**: Spec FR-011 requires meaningful empty states.
  Different messages help users understand whether the issue is
  missing data or overly restrictive filters.

## Backend API Reference

### GET /api/items

Returns scraped items, optionally filtered.

**Query Parameters**:
- `category` (optional string): Filter by category
- `status` (optional string): Filter by status

**Response** (`200 OK`):
```json
{
  "items": [
    {
      "id": "string",
      "sourceName": "string",
      "url": "string",
      "scrapeDate": "string (ISO timestamp)",
      "status": "string",
      "scrapedData": "object|array",
      "summary": "string (optional)",
      "category": "string (derived from URL domain)"
    }
  ]
}
```

### GET /api/filters

Returns distinct filter values for populating sidebar dropdowns.

**Response** (`200 OK`):
```json
{
  "categories": ["string", ...],
  "statuses": ["string", ...]
}
```

### GET /

Serves `static/index.html` as `FileResponse`.

## Static File Serving Note

The backend needs a `StaticFiles` mount to serve CSS/JS assets:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
```

This is a one-line addition to `main.py`. HTML references would use
paths like `/static/css/styles.css` and `/static/js/app.js`.
