# Quickstart: Manage Sources

**Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

## Prerequisites

- Python 3.11+ with the backend dependencies installed
  (`pip install -r requirements.txt`)
- The FastAPI backend (`main.py`) must be runnable
- CosmosDB must be accessible
- A modern desktop browser (Chrome, Firefox, Edge, or Safari)
- A valid `.xlsx` configuration file for testing uploads

## Setup

The feature extends the existing `static/` files. No additional setup
beyond what feature 001 (News Feed UI) already provides.

## Running

Start the backend server:

```bash
cd c:\prasanna\TrainingPlan\ScrapingAgent\APP_SERVICE\scrapingAgent
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open a browser and navigate to `http://localhost:8000/`.

## Validation Scenarios

### VS-001: Manage Sources button visible (FR-001)

1. Open `http://localhost:8000/`
2. **Expected**: A "Manage Sources" button is visible in the top-right
   area of the navigation bar.

### VS-002: Modal opens on click (FR-002, SC-001)

1. Click the "Manage Sources" button.
2. **Expected**: A modal overlay appears with a file upload control
   and a data table area. The background content is dimmed.

### VS-003: Upload valid Excel file (FR-003, FR-004, FR-005)

1. In the modal, click the upload control and select a valid `.xlsx`
   file.
2. **Expected**: The file is sent to the backend. A progress indicator
   (spinner or "Scraping in progress..." message) is visible. The
   upload button is disabled during the operation.

### VS-004: Scrape success feedback (FR-006, SC-003)

1. Wait for the scrape to complete successfully.
2. **Expected**: A success message appears (e.g., "Scrape completed
   successfully"). The data table refreshes to show the newly scraped
   entries.

### VS-005: Scrape error feedback (FR-007)

1. Upload an invalid `.xlsx` file (e.g., missing required columns).
2. **Expected**: An error message is displayed with details about
   what went wrong.

### VS-006: File validation (FR-010)

1. Attempt to upload a non-.xlsx file (e.g., a .txt or .csv file).
2. **Expected**: The file is rejected. A validation message indicates
   only .xlsx files are accepted.

### VS-007: Source data table (FR-008, FR-009, SC-002, SC-004)

1. Open the modal after data has been scraped.
2. **Expected**: A table displays all scraped records within 2 seconds,
   with columns: Source ID, Source Name, Status, and Scrape Date.
   All records from the backend are visible.

### VS-008: Empty table state (US2 acceptance scenario 2)

1. Open the modal when no data has been scraped (or after deleting
   all data).
2. **Expected**: A message like "No sources have been added yet"
   appears instead of an empty table.

### VS-009: Duplicate submission prevention (FR-011)

1. Upload a file. While the scrape is in progress, try to upload
   another file.
2. **Expected**: The upload button is disabled. The user cannot
   trigger a second scrape.

### VS-010: Close modal (FR-012)

1. Open the Manage Sources modal.
2. Click the close button (X) or click outside the modal.
3. **Expected**: The modal closes. The main news feed view is
   fully visible and functional.
