# Agent Instructions for Remotejobs Public Platform

This repository is a monorepo containing a Next.js frontend and a FastAPI backend.
When working in this repository, autonomous agents must always respect the boundaries of the architecture:

- **Frontend tasks** should strictly remain inside the `frontend/` directory.
- **Backend tasks** should strictly remain inside the `backend/` directory.
- **Source of Truth**: Always refer to `ARCHITECTURE.md` before making structural, database, or LLM-related changes.

## Technology Stack
- **Frontend**: Next.js (App Router), React, Tailwind CSS, TypeScript
- **Backend**: FastAPI, Pydantic v2, SQLAlchemy/SQLModel, Python (managed by `uv`)
- **Database**: PostgreSQL
