<!--
SYNC IMPACT REPORT
Version change: 0.0.0 → 1.0.0
Modified principles: N/A (initial population)
Added sections:
  - Core Principles (5 principles populated)
  - Technology Constraints (new section)
  - Development Workflow (new section)
  - Governance (populated)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ No updates needed (generic Constitution Check section adapts dynamically)
  - .specify/templates/spec-template.md: ✅ No updates needed (already aligned with requirements-driven approach)
  - .specify/templates/tasks-template.md: ✅ No updates needed (phase structure compatible with principles)
Follow-up TODOs: None
-->

# ScrapingAgent UI Constitution

## Core Principles

### I. Simplicity First

- All frontend code MUST use plain HTML, CSS, and JavaScript.
  No frameworks, transpilers, or build tools unless a concrete,
  documented requirement demands it.
- Follow YAGNI: every file, function, and abstraction MUST serve
  a current requirement. Speculative code is prohibited.
- Prefer inline or co-located styles over complex CSS architectures.
  A single stylesheet is acceptable for the entire UI.
- Rationale: The project is a lightweight frontend for an existing
  backend. Minimal tooling reduces onboarding friction, build
  complexity, and maintenance burden.

### II. Backend Integration

- The UI MUST treat the FastAPI backend as the single source of
  truth for all data and filter values.
- All API calls MUST include error handling that surfaces
  user-friendly messages when the backend is unreachable or
  returns errors.
- The UI MUST NOT cache, transform, or duplicate backend data
  beyond what is needed for immediate display and filtering.
- API endpoint paths and response shapes MUST be documented in
  contract files when a plan is produced.
- Rationale: Tight, well-defined backend coupling ensures data
  consistency and keeps the frontend stateless and simple.

### III. User Experience

- Page load to visible content MUST complete within 3 seconds
  on a standard desktop connection.
- Filter interactions MUST update the displayed feed within
  2 seconds without a full page reload.
- The three-region layout (top bar, left sidebar, right feed)
  MUST render correctly on viewports 1024px and wider.
- Empty states and error states MUST always display a clear,
  contextual message rather than a blank area.
- Rationale: Users are reviewing regulatory content under time
  pressure. Fast, predictable interactions reduce friction and
  build trust in the tool.

### IV. Code Quality

- All code MUST be readable without comments explaining
  obvious logic. Use descriptive variable and function names.
- Functions MUST have a single responsibility. Files MUST
  not exceed 300 lines; split when approaching this limit.
- JavaScript MUST use strict mode. No global variables except
  for a single application namespace if needed.
- CSS class names MUST follow a consistent naming convention
  (e.g., BEM or simple descriptive kebab-case).
- Rationale: The absence of framework guardrails means code
  discipline is the primary defense against technical debt.

### V. Progressive Delivery

- Features MUST be implemented in user-story order (P1 before
  P2 before P3) so that each increment is independently
  demonstrable and testable.
- Each user story MUST be deployable on its own without
  breaking prior stories.
- Static files MUST be servable by the existing FastAPI static
  file configuration with zero additional infrastructure.
- Rationale: Incremental delivery lets stakeholders validate
  direction early and reduces the risk of large integration
  failures.

## Technology Constraints

- **Language**: JavaScript (ES6+), HTML5, CSS3. No TypeScript,
  no preprocessors.
- **Backend**: Existing FastAPI application. The UI MUST NOT
  require backend modifications beyond serving static files.
- **Deployment**: Static files placed in the `static/` directory,
  served by FastAPI's built-in static file middleware.
- **Browser Support**: Modern desktop browsers (Chrome, Firefox,
  Edge, Safari). Mobile/responsive layout is out of scope.
- **Dependencies**: Zero external JavaScript libraries unless a
  specific, justified exception is documented and approved.

## Development Workflow

- Every feature begins with a specification (`/speckit-specify`)
  before any code is written.
- Implementation follows the plan's phase order: Setup,
  Foundational, then User Stories by priority.
- Each completed user story MUST be manually verified against
  its acceptance scenarios before proceeding to the next.
- Commits MUST be atomic: one logical change per commit with
  a descriptive message.
- Code review (self or peer) MUST check compliance with all
  five core principles before merging.

## Governance

- This constitution supersedes conflicting guidance in any
  other project document.
- Amendments require: (1) a written proposal describing the
  change and rationale, (2) an updated constitution version,
  and (3) a review of all dependent templates for consistency.
- Version numbering follows semantic versioning:
  MAJOR for principle removals or redefinitions,
  MINOR for new principles or material expansions,
  PATCH for clarifications and typo fixes.
- All specification and planning activities MUST verify
  compliance with these principles at the Constitution Check
  gate in the plan template.

**Version**: 1.0.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-06-27
