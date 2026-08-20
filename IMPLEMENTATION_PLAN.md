# Phase 1: MVP Implementation Plan

This document outlines the step-by-step execution plan to build the foundations of the public AI Job Application Platform, as defined in `ARCHITECTURE.md`.

## Step 1: Monorepo Scaffolding & Tooling
- **Backend**: Create a `backend/` folder. Initialize a modern Python environment using `uv`. Install FastAPI, Uvicorn, SQLAlchemy, and Alembic.
- **Frontend**: Create a `frontend/` folder. Initialize a Next.js (App Router) project with Tailwind CSS and TypeScript.

## Step 2: Database Schema & Domain Models
- **Database**: Ensure a local PostgreSQL instance is running.
- **Models**: Create the SQLAlchemy ORM models based on the architecture (e.g., `User`, `CandidateProfile`, `EvidenceItem`, `Job`, `JobMatch`).
- **Schemas**: Create the corresponding Pydantic schemas (v2) for API responses and LLM structured outputs.
- **Migrations**: Generate and run the first Alembic migration to create the tables.

## Step 3: Core Backend Services
- **Authentication**: Set up basic JWT auth middleware (or stub out Clerk/Supabase Auth integration) to secure routes.
- **Profile Service**: Build FastAPI endpoints to upload a CV, extract data (mocking the LLM temporarily), and save it to the `EvidenceBank`.
- **Job Source Abstraction**: Port the Arbeitnow fetching logic from the CLI into the new `JobSource` Protocol, including deduplication logic before saving to PostgreSQL.

## Step 4: Frontend Development
- **Design System**: Initialize `shadcn/ui` and configure Tailwind.
- **Pages**:
  - `/dashboard`: High-level overview of matched jobs.
  - `/profile`: Interface for users to view and edit their extracted `CandidateProfile` and `EvidenceBank`.
  - `/jobs`: A feed of jobs fetched from the API.

## Step 5: Integration & Verification
- Wire the Next.js frontend to the FastAPI backend (configure CORS).
- Verify the end-to-end flow: User can view their profile and see fetched jobs from the database.
