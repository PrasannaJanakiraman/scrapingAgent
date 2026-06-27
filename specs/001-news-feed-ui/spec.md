# Feature Specification: News Feed UI

**Feature Branch**: `001-news-feed-ui`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Create a new UI for an existing FastAPI backend. The UI should use HTML, CSS, and JavaScript with the following layout: Top navigation bar, Left sidebar with filter options for Category and State, Right side main content area with a lengthy news feed style layout. The UI should connect to the existing FastAPI backend to fetch and display data. Filters should dynamically update the news feed when selected."

## Clarifications

### Session 2026-06-27

- Q: What is the layout structure of each item in the main content area? → A: Each item is displayed as a rectangular card box with: title at the top, a 2-line summary below, and category and state shown in breadcrumb style at the bottom (e.g., "Category > State").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Scraped Content Feed (Priority: P1)

As a user, I want to view all scraped regulatory content as rectangular card boxes so that I can quickly scan titles, summaries, and metadata at a glance.

**Why this priority**: The card-based content area is the core value proposition of the UI. Without it, no other feature (filtering, navigation) has meaning. This delivers immediate value by making scraped data visually accessible in a compact format.

**Independent Test**: Can be fully tested by loading the page and verifying that scraped items appear as rectangular cards, each displaying a title, a 2-line summary, and a breadcrumb trail showing category and state.

**Acceptance Scenarios**:

1. **Given** the backend has scraped items stored, **When** the user opens the application, **Then** all items are displayed as rectangular card boxes, each showing: title at the top, a 2-line summary below, and category and state in breadcrumb style (e.g., "Category > State") at the bottom.
2. **Given** the backend has no scraped items, **When** the user opens the application, **Then** a friendly empty-state message is displayed indicating no data is available.
3. **Given** many items exist, **When** the user scrolls down, **Then** additional cards are visible in the scrollable content area.

---

### User Story 2 - Filter Content by Category (Priority: P2)

As a user, I want to filter the news feed by category so that I can focus on content from specific regulatory sources.

**Why this priority**: Category filtering is the primary way users will narrow down content. Categories are derived from source URLs and represent distinct regulatory bodies or data sources.

**Independent Test**: Can be tested by selecting a category from the sidebar and verifying only items matching that category appear in the feed.

**Acceptance Scenarios**:

1. **Given** the feed displays all items, **When** the user selects a category from the sidebar, **Then** only items belonging to that category are shown in the feed.
2. **Given** a category filter is active, **When** the user clears the category filter, **Then** all items are shown again.
3. **Given** a category filter is active, **When** the user selects a different category, **Then** the feed updates to show only items from the newly selected category.

---

### User Story 3 - Filter Content by Status (Priority: P2)

As a user, I want to filter the news feed by status (referred to as "State" in the sidebar) so that I can review items based on their scraping outcome.

**Why this priority**: Status filtering lets users separate successfully scraped content from failed or pending items, which is essential for data quality review.

**Independent Test**: Can be tested by selecting a status value from the sidebar and verifying only items with that status appear.

**Acceptance Scenarios**:

1. **Given** the feed displays all items, **When** the user selects a status from the sidebar, **Then** only items with that status are shown.
2. **Given** both category and status filters are active, **When** the user views the feed, **Then** only items matching both filters are displayed.
3. **Given** filters are active, **When** the user clears all filters, **Then** the complete unfiltered feed is restored.

---

### User Story 4 - Navigate with Top Bar (Priority: P3)

As a user, I want a persistent top navigation bar displaying the application identity so that I always know where I am and can orient myself within the application.

**Why this priority**: The navigation bar provides branding and structure but is not functionally critical to the core data browsing experience.

**Independent Test**: Can be tested by verifying the navigation bar is visible at the top of every page view, displays the application name, and remains fixed during scrolling.

**Acceptance Scenarios**:

1. **Given** the user is on the application, **When** the page loads, **Then** a top navigation bar is visible showing the application name/logo.
2. **Given** the user scrolls down through the feed, **When** they look at the top of the viewport, **Then** the navigation bar remains fixed and visible.

---

### Edge Cases

- What happens when the backend is unreachable or returns an error? The UI should display a user-friendly error message rather than a blank screen.
- What happens when a filter combination returns zero results? The feed area should display a contextual "no matching items" message.
- What happens when item content (summary/body text) is very long? Content should be truncated with an option to expand or view more.
- What happens when the filter dropdown values change between page loads (new categories appear after a fresh scrape)? Filter options should be fetched dynamically each time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The UI MUST render a fixed top navigation bar displaying the application name.
- **FR-002**: The UI MUST render a left sidebar containing filter controls for "Category" and "State" (status).
- **FR-003**: The UI MUST render a main content area on the right side displaying scraped items as rectangular card boxes.
- **FR-004**: The UI MUST fetch available filter values (categories and statuses) from the backend on page load.
- **FR-005**: The UI MUST fetch and display scraped items from the backend on page load.
- **FR-006**: When a user selects a Category filter, the news feed MUST update to show only items matching that category without a full page reload.
- **FR-007**: When a user selects a State filter, the news feed MUST update to show only items matching that status without a full page reload.
- **FR-008**: Category and State filters MUST be combinable (both active simultaneously).
- **FR-009**: The UI MUST provide a way to clear active filters and return to the full unfiltered feed.
- **FR-010**: Each card MUST display: title at the top, a 2-line summary below, and category and state in breadcrumb style (e.g., "Category > State") at the bottom.
- **FR-011**: The UI MUST display a meaningful empty state when no items match the current filters or when no data exists.
- **FR-012**: The UI MUST display a user-friendly error message when the backend is unreachable.
- **FR-013**: The UI MUST be built using plain HTML, CSS, and JavaScript (no frameworks).
- **FR-014**: The UI MUST be served as static files by the existing FastAPI backend.

### Key Entities

- **Scraped Item**: A single piece of scraped content with attributes: source name, source URL, scrape date, status, scraped data content, and summary. Categorized by its source URL domain.
- **Category**: A grouping derived from the source URL domain name, used to organize items in the feed.
- **Status (State)**: The outcome of the scraping process for an item (e.g., success, failed), used as a filter dimension.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the full list of scraped items within 3 seconds of opening the application.
- **SC-002**: Selecting a filter updates the displayed feed within 2 seconds.
- **SC-003**: The layout correctly displays the three-region structure (top bar, left sidebar, right feed) on standard desktop screen sizes (1024px and above).
- **SC-004**: 100% of scraped items returned by the backend are visible in the unfiltered feed view.
- **SC-005**: Users can identify the title, summary, category, and state of each item at a glance from the card without clicking or expanding.

## Assumptions

- Users access the application from a desktop browser with a screen width of 1024px or above. Mobile/responsive layout is out of scope for this version.
- The existing FastAPI backend endpoints (`/api/items` and `/api/filters`) are functional and return data in the expected format.
- The "State" filter label in the sidebar corresponds to the `status` field in the backend data.
- The volume of scraped items is manageable for a single-page load without pagination (hundreds, not tens of thousands).
- The static files will be placed in a `static/` directory and served by the existing FastAPI static file configuration.
- No user authentication is required to view the news feed.
