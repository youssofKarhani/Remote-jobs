# Phase 1 & 2: Implementation & Execution Plan

This document is the strict execution checklist for **Phase 1 (Candidate Foundation)** and **Phase 2 (Job Discovery)** as defined in `ARCHITECTURE.md`. Agents should follow this step-by-step.

## Step 1: Monorepo Scaffolding & Setup
- **Backend**: Create `backend/`. Initialize `uv`. Install FastAPI, Uvicorn, SQLAlchemy, Alembic, and `instructor`.
- **Frontend**: Create `frontend/`. Initialize Next.js (App Router), Tailwind CSS, and TypeScript.
- **UI Design System**: Initialize `shadcn/ui` in the frontend and install core primitives (Button, Card, Form, Input).

## Step 2: Database Schema (PostgreSQL)
Implement the core entity models in SQLAlchemy/SQLModel based strictly on Section 26 of `ARCHITECTURE.md`.
- **Identity & Preferences**: `User`, `CandidateProfile`, `CandidatePreference`
- **Evidence Bank**: `ExperienceRecord`, `EvidenceItem`, `Skill`, `Certification`, `Project`, `EducationRecord`
- **Jobs**: `Job`, `Company`, `JobSource`, `JobSourceRecord`
- **Migrations**: Generate and run the initial Alembic migration.

## Step 3: Backend Core Services (Phase 1)
- **Authentication**: Set up user auth routing (stubbed JWT or placeholder integration) to secure all endpoints.
- **AI Gateway**: Implement the `AIService` Protocol interface to abstract the LLM SDKs (Section 21).
- **CV Upload & Extraction Flow**:
  1. Endpoint to receive PDF/DOCX.
  2. Document text extraction.
  3. Route to AI Gateway for structured extraction into `CandidateProfile` + `EvidenceBank` models.
- **Profile Management**: Endpoints for the user to manually review, edit, and verify extracted evidence.

## Step 4: Backend Core Services (Phase 2)
- **Job Source Abstraction**: Implement `JobSource` Protocol. Create the `ArbeitnowSource` implementation.
- **Normalization & Deduplication**: Service to normalize incoming jobs into the canonical `Job` model, ensuring no duplicates via URL/title/company hashing.
- **Deterministic Filtering**: Service to compare fetched jobs against a user's `CandidatePreference` (e.g., location, job type) before any AI processing occurs.

## Step 5: Frontend Interface
Build the Next.js UI using `shadcn/ui`, `react-hook-form`, and `zod`.
- **`/cv-upload`**: A drag-and-drop interface to upload a resume and trigger the extraction pipeline.
- **`/profile`**: Form interfaces to view, edit, and verify the structured `CandidateProfile` and `EvidenceBank`.
- **`/preferences`**: UI to define deterministic constraints (Target roles, Locations, Salary, Remote/Hybrid).
- **`/jobs`**: A feed displaying the canonical, deduplicated jobs fetched from the database, filtered by the user's deterministic preferences.

## Definition of Done (Ready for Phase 3)
✅ The user has a verified professional profile independent of the original CV file.
✅ Jobs are normalized, deduplicated, stored once, and filterable per candidate via deterministic rules.
