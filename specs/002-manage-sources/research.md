# Research: Manage Sources

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Research Summary

All technical context items are resolved. The existing FastAPI backend
provides `POST /scrape` (file upload → scrape trigger) and
`GET /api/items` (retrieve all scraped items). No NEEDS CLARIFICATION
items remain.

## Decision Log

### D-001: Modal vs Side Panel

- **Decision**: Full-screen modal overlay with a semi-transparent backdrop.
- **Rationale**: A modal keeps the Manage Sources panel clearly separated
  from the news feed, matches the user expectation of a temporary action
  (upload, review, close). It overlays the existing three-region layout
  without disrupting it.
- **Alternatives considered**: Side drawer (right-slide panel) — rejected
  because it would conflict with the existing CSS Grid layout and require
  reworking the main content area width. Dedicated route/page — rejected
  per Constitution Principle I (no routing library, single-page app).

### D-002: File Upload Pattern

- **Decision**: Use a native HTML `<input type="file" accept=".xlsx">`
  element styled as a button. On file selection, immediately upload via
  `fetch()` with `FormData`.
- **Rationale**: Native file input is the simplest approach with zero
  dependencies. The `accept` attribute provides client-side file type
  filtering. `FormData` is the standard way to upload files via `fetch()`.
- **Alternatives considered**: Drag-and-drop upload zone — rejected as
  over-engineering for a single-file upload use case per YAGNI principle.
  Third-party upload library — rejected per zero-dependency constraint.

### D-003: Scrape API Integration

- **Decision**: POST the file to `/scrape` using `fetch()` with
  `FormData`. Show a spinner/progress indicator during the request.
  Display success or error message on completion. The backend already
  uses `_crawl_lock` to prevent concurrent scrapes, returning a 500
  if a scrape is already in progress.
- **Rationale**: The backend endpoint is already fully implemented and
  tested. The UI only needs to handle the HTTP request lifecycle
  (loading, success, error).
- **Note**: The scrape endpoint can take significant time. The UI should
  disable the upload button and show progress while waiting. If the
  backend returns a lock error (concurrent scrape), the UI should display
  "A scrape is already in progress."

### D-004: Source Data Table

- **Decision**: Use a plain HTML `<table>` element with four columns
  (Source ID, Source Name, Status, Scrape Date). Data fetched from the
  existing `GET /api/items` endpoint.
- **Rationale**: The endpoint already returns all necessary fields
  (`sourceId`, `sourceName`, `status`, `scrapeDate`). A simple HTML
  table is the lightest-weight approach per Constitution Principle I.
- **Alternatives considered**: CSS Grid-based table layout — rejected
  as unnecessary when a semantic `<table>` element is more accessible
  and simpler. Virtual scrolling — rejected since the dataset is
  small (hundreds of rows).

### D-005: Date Formatting

- **Decision**: Format `scrapeDate` (ISO 8601 string) using
  `new Date(scrapeDate).toLocaleString()` for user-friendly display.
- **Rationale**: `toLocaleString()` is built into JavaScript, requires
  no libraries, and respects the user's locale settings.

## Backend API Reference

### POST /scrape

Uploads an Excel config file and triggers scraping.

**Request**: `multipart/form-data` with field `file` (UploadFile)

**Response** (`200 OK`):
```json
{
  "total_pages": 5,
  "total_index_pages": 1,
  "results": [
    {
      "source_url": "string",
      "title": "string",
      "meta_description": "string",
      "body_text": "string",
      "status": "string",
      "link_text": "string",
      "link_context": "string"
    }
  ]
}
```

**Error responses**:
- `400 Bad Request`: Non-.xlsx file uploaded
- `422 Unprocessable Entity`: Could not parse Excel or no valid rows
- `500 Internal Server Error`: Crawler error or concurrent scrape lock

### GET /api/items

Returns all scraped items (same endpoint used by the news feed).

See `specs/001-news-feed-ui/contracts/api-contracts.md` for full
response schema. Relevant table fields:
- `sourceId` → Source ID column
- `sourceName` → Source Name column
- `status` → Status column
- `scrapeDate` → Scrape Date column
