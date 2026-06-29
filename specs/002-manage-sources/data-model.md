# Data Model: Manage Sources

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Overview

The Manage Sources feature does not define new persistent data. It
reuses the existing CosmosDB scraped items returned by `GET /api/items`
and uploads files to `POST /scrape`. This document describes the data
shapes relevant to the modal's table display and upload flow.

## Entities

### SourceTableRow

A row in the Manage Sources data table, derived from a scraped item.

| Field | Type | Source | UI Column |
|-------|------|--------|-----------|
| sourceId | string | CosmosDB partition key | Source ID |
| sourceName | string | Derived from source URL | Source Name |
| status | string | Scrape outcome | Status |
| scrapeDate | string (ISO) | Timestamp of scrape | Scrape Date |

**Display rules**:
- `scrapeDate` is formatted to user-locale string via `toLocaleString()`
- `sourceName` falls back to "Unknown" if empty/null
- `status` displayed as-is (e.g., "success", "failed")

### UploadState (client-side only)

Runtime state for the file upload flow. Not persisted.

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| isUploading | boolean | false | Disables upload button, shows spinner |
| uploadError | string/null | null | Error message from scrape attempt |
| uploadSuccess | boolean | false | Shows success banner after scrape |
| selectedFile | File/null | null | The file selected by the user |

### ModalState (client-side only)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| isOpen | boolean | false | Controls modal visibility |

## Relationships

```text
File input → selectedFile → FormData → POST /scrape
POST /scrape response → uploadSuccess/uploadError → refresh table
GET /api/items response → SourceTableRow[] → rendered as <table> rows
```

## Validation Rules

- File MUST have `.xlsx` extension (client-side `accept` attribute +
  JS validation before upload)
- Upload MUST be blocked when `isUploading` is true (prevents
  duplicate submissions per FR-011)
- Table MUST gracefully handle empty data with a "No sources added
  yet" message
