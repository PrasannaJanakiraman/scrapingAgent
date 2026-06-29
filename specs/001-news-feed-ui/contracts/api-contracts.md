# API Contracts: News Feed UI

**Date**: 2026-06-27 | **Spec**: [spec.md](../spec.md)

## Overview

The frontend consumes two existing backend endpoints. These contracts
document the expected request/response shapes that the frontend
depends on. The backend already implements these endpoints in
`main.py`.

---

## GET /api/filters

Fetch available filter values for the sidebar dropdowns.

**Request**: No parameters.

**Response** (`200 OK`):
```json
{
  "categories": ["regulatory-body-1.gov", "agency-2.org"],
  "statuses": ["success", "failed", "pending"]
}
```

**Response fields**:
| Field | Type | Description |
|-------|------|-------------|
| categories | string[] | Distinct category values from all items |
| statuses | string[] | Distinct status values from all items |

**Error responses**:
- `500 Internal Server Error`: Backend/database error. Frontend
  displays error banner and disables filter dropdowns.

**Frontend usage**: Called once on page load. Results populate the
Category and State dropdown menus. An "All" option is prepended
client-side.

---

## GET /api/items

Fetch scraped items, optionally filtered by category and/or status.

**Request query parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter items by category |
| status | string | No | Filter items by status |

**Example requests**:
- `GET /api/items` — all items
- `GET /api/items?category=regulatory-body.gov` — filtered by category
- `GET /api/items?status=success` — filtered by status
- `GET /api/items?category=regulatory-body.gov&status=success` — both

**Response** (`200 OK`):
```json
{
  "items": [
    {
      "id": "abc123",
      "sourceId": "src-001",
      "sourceName": "Regulatory Body Notice #42",
      "url": "https://regulatory-body.gov/notice/42",
      "scrapeDate": "2026-06-25T14:30:00Z",
      "status": "success",
      "scrapedData": {},
      "summary": "New regulation regarding data privacy...",
      "category": "regulatory-body.gov"
    }
  ]
}
```

**Response fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| items | array | No | Array of scraped item objects |
| items[].id | string | No | Unique document identifier |
| items[].sourceId | string | No | Partition key (not displayed) |
| items[].sourceName | string | No | Human-readable source name |
| items[].url | string | No | Original source URL |
| items[].scrapeDate | string | No | ISO 8601 timestamp |
| items[].status | string | No | Scrape outcome (e.g., success, failed) |
| items[].scrapedData | object | No | Raw scraped content (not displayed) |
| items[].summary | string | Yes | LLM-generated summary text |
| items[].category | string | No | Derived from URL domain |

**Error responses**:
- `500 Internal Server Error`: Backend/database error. Frontend
  displays error banner in the content area.

**Frontend usage**: Called on page load (no filters) and on each
filter change (with query parameters). Response items are rendered
as cards in the main content area.

---

## GET /

Serves the frontend entry point.

**Response** (`200 OK`): Returns `static/index.html` as an HTML file
response.

**Frontend usage**: Browser navigates to this URL to load the
application. The HTML file references `/static/css/styles.css` and
`/static/js/app.js`.

---

## Static Assets

**Mount point**: `/static` (requires `StaticFiles` mount in backend)

**Assets served**:
| Path | File |
|------|------|
| `/static/css/styles.css` | Main stylesheet |
| `/static/js/app.js` | Main JavaScript file |

**Backend requirement**: A one-line addition to `main.py`:
```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```
