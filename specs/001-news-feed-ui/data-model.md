# Data Model: News Feed UI

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Overview

The frontend does not define its own persistent data model. All data
originates from the FastAPI backend (CosmosDB). This document describes
the data shapes the frontend receives and renders.

## Entities

### ScrapedItem

A single piece of scraped regulatory content displayed as a card
in the news feed.

| Field | Type | Source | UI Usage |
|-------|------|--------|----------|
| id | string | CosmosDB document ID | Internal key for DOM elements |
| sourceName | string | Derived from source URL | Displayed as card title |
| url | string | Original source URL | Available for linking (future) |
| scrapeDate | string (ISO) | Timestamp of scrape | Not displayed in v1 |
| status | string | Scrape outcome | Breadcrumb trail + State filter |
| scrapedData | object/array | Raw scraped content | Not displayed directly |
| summary | string (optional) | LLM-generated summary | 2-line summary on card |
| category | string | Derived from URL domain | Breadcrumb trail + Category filter |

**Card mapping**:
- Title: `sourceName`
- Summary: `summary` (truncated to 2 lines via CSS)
- Breadcrumb: `category` > `status` (e.g., "regulatory-body.gov > success")

**Fallbacks**:
- If `summary` is empty/null: display "No summary available"
- If `sourceName` is empty/null: display the `url` truncated

### FilterOptions

The set of available filter values fetched once on page load.

| Field | Type | UI Usage |
|-------|------|----------|
| categories | string[] | Populates Category dropdown in sidebar |
| statuses | string[] | Populates State dropdown in sidebar |

**Behavior**:
- Filter values are fetched from `GET /api/filters` on page load
- Dropdowns include an "All" option (added client-side) as the
  default selection
- Selecting a value triggers a re-fetch of items with query params

### UIState (client-side only)

Runtime state managed in JavaScript variables. Not persisted.

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| selectedCategory | string/null | null | Active category filter |
| selectedStatus | string/null | null | Active status filter |
| items | ScrapedItem[] | [] | Currently displayed items |
| isLoading | boolean | false | Controls loading indicator |
| error | string/null | null | Current error message |

## Relationships

```text
FilterOptions.categories ──► selectedCategory ──► GET /api/items?category=X
FilterOptions.statuses   ──► selectedStatus   ──► GET /api/items?status=Y
GET /api/items response  ──► items[]          ──► rendered as cards
```

## Validation Rules

- No client-side validation of data shapes. The backend is the
  single source of truth (Constitution Principle II).
- The UI MUST gracefully handle missing or null fields by showing
  fallback text rather than crashing.
- Filter values MUST be fetched fresh on each page load to reflect
  new categories/statuses from recent scrapes.
