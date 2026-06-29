# API Contracts: Manage Sources

**Date**: 2026-06-27 | **Spec**: [spec.md](../spec.md)

## Overview

The Manage Sources feature consumes two existing backend endpoints.
No new backend endpoints are required. This document describes the
request/response shapes the frontend depends on for the upload flow
and table display.

---

## POST /scrape

Upload an Excel configuration file and trigger scraping of all
configured URLs.

**Request**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File (.xlsx) | Yes | Excel configuration file |

**Example request** (JavaScript):
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);
const response = await fetch("/scrape", { method: "POST", body: formData });
```

**Response** (`200 OK`):
```json
{
  "total_pages": 5,
  "total_index_pages": 1,
  "results": [
    {
      "source_url": "https://example.gov/regulation",
      "title": "Example Regulation",
      "meta_description": "...",
      "body_text": "...",
      "status": "success",
      "link_text": "",
      "link_context": ""
    }
  ]
}
```

**Error responses**:

| Status | Detail | Frontend Handling |
|--------|--------|-------------------|
| 400 | "Only .xlsx files are accepted." | Display validation error |
| 422 | "Could not parse Excel file: ..." | Display parse error |
| 422 | "No valid rows found..." | Display empty-data error |
| 500 | "Crawler error: ..." | Display scrape failure error |

**Frontend usage**: Called when user uploads a file in the Manage Sources
modal. Response triggers table refresh on success, or error banner on
failure.

**Note**: The backend uses `_crawl_lock` to prevent concurrent scrapes.
If a scrape is already running, the request will block until the lock
is released (not return immediately). The frontend prevents duplicate
submissions via the `isUploading` flag.

---

## GET /api/items

Fetch all scraped items for the source data table.

**Request**: No parameters required (table shows all items unfiltered).

**Response** (`200 OK`):
```json
{
  "items": [
    {
      "id": "abc123",
      "sourceId": "src-001",
      "sourceName": "Regulatory Body",
      "url": "https://regulatory-body.gov/",
      "scrapeDate": "2026-06-25T14:30:00Z",
      "status": "success",
      "scrapedData": {},
      "summary": "...",
      "category": "Regulatory-Body"
    }
  ]
}
```

**Table column mapping**:

| Table Column | Response Field | Formatting |
|-------------|----------------|------------|
| Source ID | `sourceId` | As-is |
| Source Name | `sourceName` | As-is, fallback "Unknown" |
| Status | `status` | As-is |
| Scrape Date | `scrapeDate` | `new Date(scrapeDate).toLocaleString()` |

**Frontend usage**: Called when the Manage Sources modal opens and after
each successful scrape to refresh the table.
