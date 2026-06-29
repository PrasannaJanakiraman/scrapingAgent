# Feature Specification: Manage Sources

**Feature Branch**: `002-manage-sources`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Create a manage source button on top right side nav bar and for this have upload excel file option over there after user uploading it should call the scrape api and below that one table will have the added data with columns name source id, sourcename, status, scrapedate"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Excel Configuration File (Priority: P1)

As a user, I want to upload an Excel configuration file from the navigation bar so that the system scrapes the configured sources and stores the results.

**Why this priority**: Uploading and triggering a scrape is the core action of this feature. Without it, the data table has nothing to display. This is the primary user workflow that delivers immediate value.

**Independent Test**: Can be fully tested by clicking "Manage Sources", selecting a valid .xlsx file, and verifying the scrape executes successfully with a confirmation message.

**Acceptance Scenarios**:

1. **Given** the user is on the application, **When** they click the "Manage Sources" button in the top-right of the navigation bar, **Then** a panel or modal appears with an option to upload an Excel file.
2. **Given** the upload panel is open, **When** the user selects a valid .xlsx file and confirms, **Then** the system triggers the scrape process and displays a progress indicator while scraping is in progress.
3. **Given** the scrape process completes successfully, **When** the user views the result, **Then** a success message is shown and the source data table is updated with the newly scraped data.
4. **Given** the scrape process fails, **When** the user views the result, **Then** a user-friendly error message is displayed explaining what went wrong.
5. **Given** the upload panel is open, **When** the user selects a non-.xlsx file, **Then** the system rejects the file and displays a validation message indicating only .xlsx files are accepted.

---

### User Story 2 - View Source Data Table (Priority: P2)

As a user, I want to see a table of all scraped source data so that I can review the scrape history and status of each source.

**Why this priority**: The table provides visibility into what has been scraped and its status. It depends on having data from the upload/scrape flow (US1) but is essential for users to track and verify their sources.

**Independent Test**: Can be tested by opening the Manage Sources panel and verifying the table displays all previously scraped items with the correct columns and data.

**Acceptance Scenarios**:

1. **Given** the user opens the Manage Sources panel, **When** scraped data exists, **Then** a table is displayed with columns: Source ID, Source Name, Status, and Scrape Date.
2. **Given** the user opens the Manage Sources panel, **When** no scraped data exists, **Then** the table area displays a message indicating no sources have been added yet.
3. **Given** new data has been scraped via file upload, **When** the scrape completes, **Then** the table automatically refreshes to include the new entries.

---

### Edge Cases

- What happens when the user uploads a file while a scrape is already in progress? The system should indicate that a scrape is already running and prevent a duplicate submission.
- What happens when the Excel file contains no valid rows? The system should display a clear error message indicating the file was parsed but contained no valid source configurations.
- What happens when the user closes the Manage Sources panel during an active scrape? The scrape should continue in the background; reopening the panel should show the updated status.
- What happens when the source data table has many rows? The table should be scrollable within the panel without affecting the main page layout.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The UI MUST display a "Manage Sources" button in the top-right area of the navigation bar.
- **FR-002**: Clicking the "Manage Sources" button MUST open a panel or modal overlay for source management.
- **FR-003**: The source management panel MUST include a file upload control that accepts only .xlsx files.
- **FR-004**: Upon file upload, the system MUST send the file to the backend scrape endpoint and trigger the scraping process.
- **FR-005**: The UI MUST display a progress indicator while the scrape operation is in progress.
- **FR-006**: Upon successful scrape completion, the UI MUST show a success message and refresh the data table.
- **FR-007**: Upon scrape failure, the UI MUST display a user-friendly error message with details about the failure.
- **FR-008**: The source management panel MUST display a data table with columns: Source ID, Source Name, Status, and Scrape Date.
- **FR-009**: The data table MUST load all existing scraped source records when the panel opens.
- **FR-010**: The UI MUST validate the uploaded file is a .xlsx file before sending it to the backend.
- **FR-011**: The UI MUST prevent duplicate scrape submissions while a scrape is already in progress.
- **FR-012**: The source management panel MUST be closable, returning the user to the main news feed view.

### Key Entities

- **Scrape Source**: A record representing a scraped data source with attributes: source ID (unique identifier), source name (human-readable name derived from the URL), status (outcome of the scrape — e.g., success, failed), and scrape date (timestamp of when the scrape occurred).
- **Excel Configuration File**: A .xlsx file uploaded by the user containing source URLs and scraping rules that define what to scrape and how.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload an Excel file and trigger a scrape within 3 clicks from the main page (click Manage Sources → select file → confirm upload).
- **SC-002**: The source data table displays all scraped records within 2 seconds of opening the panel.
- **SC-003**: Users receive clear feedback (success or error) within 5 seconds of a scrape completing.
- **SC-004**: 100% of scraped source records are visible in the data table with correct Source ID, Source Name, Status, and Scrape Date values.

## Assumptions

- The existing backend scrape endpoint accepts .xlsx files and returns scrape results. No backend changes are required beyond what already exists.
- The existing backend data retrieval endpoint provides all fields needed for the table (source ID, source name, status, scrape date).
- The "Manage Sources" panel is part of the same single-page application and does not require a separate page or route.
- The scrape operation may take a significant amount of time (seconds to minutes) depending on the number of URLs in the Excel file, so asynchronous feedback is important.
- No user authentication is required — all users can upload files and view source data.
- The feature builds on the existing News Feed UI (feature 001) and extends its navigation bar.
