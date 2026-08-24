# 🚀 RemoteJobs Public Platform

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.3+-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Package Manager - UV](https://img.shields.io/badge/uv-Fast%20Python%20Packaging-DE5FE9?style=flat&logo=astral)](https://github.com/astral-sh/uv)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(188%2B%20tests)-2EA44F?style=flat&logo=pytest&logoColor=white)](https://pytest.org)

An enterprise-grade, multi-user AI job discovery and application platform built on a **deterministic anti-hallucination architecture**. The platform ingests and deduplicates jobs across multiple sources, extracts verified candidate evidence from resumes, applies zero-cost deterministic filters, and gates all LLM operations through mathematically strict validation.

---

## 💡 Core Philosophy

> **"LLMs may decide which verified evidence is relevant. They may not decide what evidence exists."**

In conventional AI job tools, generative models freely hallucinate bullet points, metrics, and technical proficiencies. **RemoteJobs** solves this at the architectural layer:
- Resumes are parsed into an **Evidence Bank** of discrete, immutable items with stable identifiers (`EXP_001`, `SKILL_001`, `PROJ_001`).
- The candidate reviews and verifies each record.
- When tailoring applications, AI models **only return verified IDs** (`selected_ids ⊆ allowed_ids`).
- The backend validates selection subsets by code and retrieves exact source text from the database to render final documents.

---

## 📑 Table of Contents

- [Core Philosophy](#-core-philosophy)
- [Key Features](#-key-features)
- [Architecture & Processing Funnel](#-architecture--processing-funnel)
- [Tech Stack](#-tech-stack)
- [Monorepo Directory Structure](#-monorepo-directory-structure)
- [Quickstart Guide](#-quickstart-guide)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Local LLM Setup (Optional / Default: Ollama)](#3-local-llm-setup-optional--default-ollama)
- [API Endpoints Overview](#-api-endpoints-overview)
- [Deterministic Filtering & Anti-Hallucination Guardrails](#-deterministic-filtering--anti-hallucination-guardrails)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [Project Roadmap](#-project-roadmap)

---

## ✨ Key Features

### 1. Canonical Candidate Profile & Evidence Bank
- **Atomic Evidence Ingestion**: Deconstructs candidate resumes (PDF, DOCX, Plain Text) into structured entities: Experience Records, Evidence Bullets, Categorized Skills (`programming`, `backend`, `ai_ml`, `devops`, `tools`, `soft_skill`), Certifications, Projects, and Education.
- **Stable ID System**: Assigns deterministic, format-validated identifiers (`^[A-Z]{3,5}_\d{3,5}$`) such as `EXP_001`, `SKILL_001`, `PROJ_001`, `CERT_001`, and `EDU_001`.
- **Pre-Approved Variants**: Supports verified alternate phrasing for achievements (e.g. `EXP_001_FULL`, `EXP_001_SHORT`, `EXP_001_DATA`) so the model can optimize layout without altering facts.
- **Draft & Verification Lifecycle**: Extracted items start as unverified drafts (`is_verified = False`) and are gated until confirmed by the user.

### 2. Multi-Source Job Discovery & Normalization
- **Job Source Abstraction**: Protocol-driven ingestion architecture (`JobSource`) decoupled from any single provider.
- **Arbeitnow Integration**: Built-in vendor mapping converting external payloads, Unix epoch timestamps, tags, and company details to canonical `Job` models.
- **Title Sanitization**: Automatically scrubs gender markers (e.g. `(m/w/d)`, `(gn)`, `(f/m/d)`) and recruitment filler phrases.

### 3. Multi-Level Deduplication Engine
- **Three-Tier De-duping**:
  1. External Source ID lookup.
  2. Canonical URL normalization (query parameters like `utm_source` and `ref` are stripped).
  3. SHA-256 composite content hashing (`norm_url|norm_title|norm_company|norm_location`).
- **Provenance Tracking**: Preserves distinct `JobSourceRecord` entries linked to a single canonical `Job` entity, avoiding duplicate database records.

### 4. Zero-Cost Deterministic Candidate Filtering
- Evaluates candidate preferences before invoking expensive AI models:
  - **Remote Policy**: Strict `remote_only` enforcement.
  - **Location Matching**: Case-insensitive and substring city/country matching.
  - **Multilingual Job Types**: Normalizes types like `"Working Student"` and `"Werkstudent"`.
  - **Regex Word Boundaries**: Precise keyword search (e.g., matching `IT` without matching `with`).
  - **Exclusion Rules**: Short-circuits matches on excluded companies or prohibited keywords.
  - **Compensation Thresholds**: Filters on minimum acceptable salary.

### 5. Strict Evidence Validation Gate
- Enforces `selected_ids ⊆ allowed_ids` mathematically on all AI outputs.
- Blocks cross-tenant evidence leakage, non-existent references (`EXP_999`), and unverified draft bullets.

---

## 🏛 Architecture & Processing Funnel

```text
                                  +-----------------------+
                                  | External Job Sources  |
                                  | (Arbeitnow, APIs, ...) |
                                  +-----------+-----------+
                                              |
                                              v
                              +-------------------------------+
                              | Multi-Level Deduplication     |
                              | (Canonical URL + SHA-256 Hash)|
                              +---------------+---------------+
                                              |
                                              v
                                  +-----------------------+
                                  | Canonical Job Model   |
                                  +-----------+-----------+
                                              |
     +-------------------+                    v
     | Candidate Profile | ----> [ Deterministic Filter ]  <--- (Locations, Roles, Remote, Exclusions)
     | & Evidence Bank   |                    |
     +---------+---------+                    v  (Passed candidates only)
               |                  +-----------------------+
               |                  | AI Pre-Screening      | (Cheap / High-Recall)
               |                  +-----------+-----------+
               |                              |
               |                              v
               |                  +-----------------------+
               |                  | AI Deep Assessment    | (Detailed multi-dimensional score)
               |                  +-----------+-----------+
               |                              |
               v                              v
    +--------------------+        +-----------------------+
    | Allowed Evidence   | -----> | AI Evidence Selection | (Selects IDs only)
    | IDs: EXP_001, ...  |        +-----------+-----------+
    +--------------------+                    |
                                              v
                              +-------------------------------+
                              | Strict Validation Gate        |
                              | selected_ids ⊆ allowed_ids    |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              | Static Document Renderer      |
                              | (Resolves text from DB)       |
                              +---------------+---------------+
                                              |
                                              v
                                      [ Tailored CV / CL ]
```

---

## 💻 Tech Stack

### Backend
- **Language**: Python 3.13+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Async ASGI)
- **Data Layer**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async/Sync ORM) with [Alembic](https://alembic.sqlalchemy.org/) migrations
- **Database**: PostgreSQL (production-ready) / SQLite (development & testing)
- **Validation & Serialization**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **AI & Extraction**: [Instructor](https://github.com/jxnl/instructor), `pypdf`, `python-docx`
- **Security**: PyJWT, passlib with bcrypt
- **Package Management**: [Astral `uv`](https://github.com/astral-sh/uv)

### Frontend
- **Framework**: [Next.js 16 (App Router)](https://nextjs.org/)
- **UI & Components**: React 19, [Tailwind CSS](https://tailwindcss.com/), [Radix UI](https://www.radix-ui.com/), [Lucide React](https://lucide.dev/)
- **Forms & Validation**: React Hook Form, [Zod](https://zod.dev/)
- **Language**: TypeScript 5.5+

### Testing & Quality
- **Test Runners**: `pytest`, `pytest-asyncio`
- **Coverage**: 4-tier opaque-box E2E suite + Unit & Adversarial migration cycles

---

## 📂 Monorepo Directory Structure

```text
remotejobs-public/
├── ARCHITECTURE.md              # Complete technical architecture specification
├── IMPLEMENTATION_PLAN.md       # Execution checklist for phases
├── TEST_READY.md                # E2E test verification report
├── pyproject.toml               # Monorepo root testing dependencies & pytest config
├── pytest.ini                   # Pytest configuration
├── uv.lock                      # Root dependency lockfile
│
├── backend/                     # FastAPI Backend Application
│   ├── alembic/                 # Database schema migrations
│   │   ├── versions/            # Version migration scripts
│   │   └── env.py
│   ├── alembic.ini              # Alembic configuration
│   ├── pyproject.toml           # Backend Python package definition
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point & CORS
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── database.py          # SQLAlchemy engine, session maker, & Base
│   │   ├── core/                # JWT auth, password hashing, security deps
│   │   ├── models/              # SQLAlchemy database entities
│   │   │   ├── user.py          # User account model
│   │   │   ├── profile.py       # CandidateProfile model
│   │   │   ├── preference.py    # CandidatePreference model
│   │   │   ├── evidence.py      # EvidenceItem, ExperienceRecord, Skill, etc.
│   │   │   └── job.py           # Job, Company, JobSource, JobSourceRecord
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── protocols/           # Abstraction protocols (JobSource, AIService)
│   │   ├── integrations/        # Concrete integrations (Arbeitnow, Ollama/OpenAI)
│   │   ├── services/            # Business domain logic
│   │   │   ├── cv_extraction_service.py # Ingestion & structured parsing
│   │   │   ├── document_parser.py       # PDF/DOCX file extractors
│   │   │   ├── evidence_validation.py   # Guardrail validation gate
│   │   │   ├── job_deduplication.py     # URL & SHA-256 deduplication
│   │   │   └── job_filtering.py         # Deterministic candidate filter
│   │   └── routers/             # API v1 route handlers
│   │       ├── auth.py          # /api/v1/auth endpoints
│   │       ├── cv.py            # /api/v1/cv endpoints
│   │       ├── profile.py       # /api/v1/profile endpoints
│   │       ├── preferences.py   # /api/v1/preferences endpoints
│   │       └── jobs.py          # /api/v1/jobs endpoints
│   └── tests/                   # Backend unit and integration tests
│
├── frontend/                    # Next.js 16 App Router Frontend
│   ├── package.json             # NPM dependencies and scripts
│   ├── tailwind.config.ts       # Tailwind CSS design system configuration
│   ├── tsconfig.json            # TypeScript configuration
│   └── src/
│       ├── app/
│       │   ├── layout.tsx       # Root layout with responsive navigation
│       │   ├── page.tsx         # Platform landing overview
│       │   ├── cv-upload/       # CV upload & ingestion interface
│       │   ├── profile/         # Evidence Bank review & management UI
│       │   ├── preferences/     # Deterministic candidate rules config UI
│       │   └── jobs/            # Deduplicated, filtered job discovery feed
│       ├── components/
│       │   ├── layout/          # Navbar, Footer, Container components
│       │   └── ui/              # Button, Card, Badge, Input, Tabs, Dialog
│       └── lib/
│           ├── api.ts           # Frontend API client methods
│           ├── api-client.ts    # Fetch wrapper with JWT header handling
│           └── constants.ts     # UI constants & enum choices
│
└── tests/                       # Monorepo End-to-End Test Suite
    └── e2e/
        ├── conftest.py          # Test database fixtures & engine
        ├── test_tier1_feature_coverage.py          # Tier 1: Canonical Feature Invariants
        ├── test_tier2_boundary_corner_cases.py      # Tier 2: Boundary & Edge Cases
        ├── test_tier3_cross_feature_interactions.py # Tier 3: Cross-Feature Flows
        ├── test_tier4_workloads_and_scenarios.py    # Tier 4: Real-World Workloads & Security
        └── test_adversarial_e2e.py                  # Adversarial injection & stress tests
```

---

## ⚡ Quickstart Guide

### Prerequisites
- **Python**: 3.13 or higher
- **Node.js**: 20.x or higher
- **uv**: Fast Python package installer (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git**

---

### 1. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies and create virtual environment**:
   ```bash
   uv sync
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in `backend/`:
   ```env
   APP_NAME="RemoteJobs Public Platform API"
   APP_VERSION="0.1.0"
   ENVIRONMENT="development"
   DEBUG=True

   # Database (PostgreSQL in production, SQLite in local dev)
   DATABASE_URL="sqlite:///./remotejobs_dev.db"

   # Security
   SECRET_KEY="your-super-secret-key-change-this-in-production"
   ACCESS_TOKEN_EXPIRE_MINUTES=10080

   # AI Gateway (Ollama local fallback)
   LLM_PROVIDER="ollama"
   LLM_BASE_URL="http://localhost:11434/v1"
   LLM_MODEL_EXTRACTION="llama3"
   LLM_MODEL_PRESCREEN="llama3"
   LLM_MODEL_ASSESSMENT="llama3"

   # CORS
   CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
   ```

4. **Run Database Migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the FastAPI Server**:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`.
   - Interactive OpenAPI Docs: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Configure Frontend Environment**:
   Create a `.env.local` file in `frontend/`:
   ```env
   NEXT_PUBLIC_API_URL="http://localhost:8000"
   ```

4. **Start the Next.js Development Server**:
   ```bash
   npm run dev
   ```

   Open `http://localhost:3000` in your browser.

---

### 3. Local LLM Setup (Optional / Default: Ollama)

The backend AI Gateway defaults to a local [Ollama](https://ollama.ai/) instance:

1. Install Ollama:
   ```bash
   # macOS / Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. Pull the default model:
   ```bash
   ollama run llama3
   ```
3. The platform will automatically communicate with Ollama at `http://localhost:11434/v1`.

---

## 📡 API Endpoints Overview

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new candidate account |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT bearer token |
| **Auth** | `GET` | `/api/v1/auth/me` | Fetch authenticated user profile details |
| **CV** | `POST` | `/api/v1/cv/upload` | Upload PDF/DOCX or plain text for structured ingestion |
| **CV** | `POST` | `/api/v1/cv/parse-text` | Ingest raw CV text directly into Evidence Bank draft |
| **Profile** | `GET` | `/api/v1/profile` | Retrieve candidate profile and full Evidence Bank |
| **Profile** | `PUT` | `/api/v1/profile` | Update profile headline, summary, and contact info |
| **Profile** | `POST` | `/api/v1/profile/evidence` | Add a new evidence item with assigned stable ID |
| **Profile** | `PUT` | `/api/v1/profile/evidence/{id}` | Update evidence content or pre-approved variants |
| **Profile** | `POST` | `/api/v1/profile/evidence/{id}/verify` | Verify draft evidence item for CV inclusion |
| **Profile** | `POST` | `/api/v1/profile/skills` | Add a new categorized skill record |
| **Profile** | `POST` | `/api/v1/profile/validate-evidence` | Test evidence ID selection gate against allowed IDs |
| **Preferences** | `GET` | `/api/v1/preferences` | Get deterministic candidate filtering rules |
| **Preferences** | `PUT` | `/api/v1/preferences` | Update filtering rules (locations, remote, exclusions) |
| **Jobs** | `GET` | `/api/v1/jobs` | Get paginated list of canonical deduplicated jobs |
| **Jobs** | `GET` | `/api/v1/jobs/feed` | Get jobs filtered by current user's preferences |
| **Jobs** | `POST` | `/api/v1/jobs/sync` | Trigger on-demand sync from external job sources |
| **Health** | `GET` | `/api/health` | Service health status check probe |

---

## 🛡 Deterministic Filtering & Anti-Hallucination Guardrails

### 1. Evidence ID Gate Validation
```python
# app/services/evidence_validation.py
def validate_selected_evidence(
    user_id: int,
    selected_ids: list[str],
    allowed_ids: set[str],
    db_session: Session
) -> list[EvidenceItem]:
    # 1. Subset invariant check: selected_ids ⊆ allowed_ids
    invalid_ids = set(selected_ids) - allowed_ids
    if invalid_ids:
        raise ValidationError(f"Unauthorized or hallucinated IDs: {invalid_ids}")

    # 2. Database ownership & verification check
    items = db_session.query(EvidenceItem).filter(
        EvidenceItem.user_id == user_id,
        EvidenceItem.stable_id.in_(selected_ids),
        EvidenceItem.is_verified == True
    ).all()

    if len(items) != len(selected_ids):
        raise ValidationError("One or more evidence IDs are unverified or cross-tenant.")

    return items
```

### 2. Multi-Level Deduplication Invariant
```python
# app/services/job_deduplication.py
def compute_content_hash(job: CanonicalJob) -> str:
    norm_url = strip_query_params(job.canonical_url)
    norm_title = sanitize_title(job.title)
    norm_company = job.company.lower().strip()
    norm_location = job.location.lower().strip()
    
    raw = f"{norm_url}|{norm_title}|{norm_company}|{norm_location}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

---

## 🧪 Testing & Quality Assurance

The project features a comprehensive test suite across the monorepo:

### Running E2E Test Suite (All Tiers)
```bash
# From workspace root
uv run pytest
```

### Running Backend Unit & Adversarial Tests
```bash
# From backend directory or workspace root
uv run pytest backend/tests
```

### Running Frontend Typecheck & Linting
```bash
cd frontend
npm run typecheck
npm run lint
```

### Test Suite Breakdown

| Tier | Category | Scope |
| :--- | :--- | :--- |
| **Tier 1** | Canonical Feature Coverage | Database models, Stable ID generation, CV parsing, Arbeitnow ingestion protocol, Deduplication engine, Deterministic filtering, Evidence gate validation. |
| **Tier 2** | Boundary & Edge Cases | Extreme payload sizes (50k+ words), German umlauts & emojis, URL tracking parameter normalization, regex meta-character keywords (`C++`, `.NET`), rate-limiting exponential backoff. |
| **Tier 3** | Cross-Feature Interactions | Full lifecycle (Register &rarr; CV Ingest &rarr; Verify &rarr; Preference Config &rarr; Ingest Jobs &rarr; Filter &rarr; Tailor), multi-tenant isolation, dynamic preference mutation. |
| **Tier 4** | Real-World Workloads & Security | Working Student journey (German/English), Senior Remote Architect journey, high-volume ingestion stress tests, adversarial prompt injection sandboxing. |

---

## ⚙️ Configuration & Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./remotejobs_dev.db` | Database connection URL (PostgreSQL in production) |
| `SECRET_KEY` | `dev-secret-key-...` | Secret used for JWT signing |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | Token expiration window |
| `LLM_PROVIDER` | `ollama` | Provider for AI extraction & evaluation (`ollama`, `openai`, `anthropic`) |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Base URL for LLM API requests |
| `LLM_API_KEY` | `ollama` | API key for LLM provider (if required) |
| `LLM_MODEL_EXTRACTION` | `llama3` | Model used for CV structure extraction |
| `LLM_MODEL_PRESCREEN` | `llama3` | Model used for high-volume job pre-screening |
| `LLM_MODEL_ASSESSMENT` | `llama3` | Model used for candidate compatibility scoring |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins for the API |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL for the Next.js frontend |

---

## 🗺 Project Roadmap

- [x] **Phase 1: Candidate Foundation**
  - Canonical database schema with PostgreSQL / SQLite support.
  - Stable Evidence ID assignment and immutability rules.
  - Resume parsing pipeline with Draft staging and user verification flow.
  - Strict evidence gate validation.
  - Full Next.js frontend for CV upload and Evidence Bank management.
- [x] **Phase 2: Job Discovery & Ingestion**
  - `JobSource` abstraction protocol.
  - `ArbeitnowSource` implementation with title normalization.
  - Multi-level deduplication (External ID, URL query stripping, SHA-256 content hashing).
  - Deterministic candidate preference filtering engine.
  - Real-time filtered jobs feed in Next.js UI.
- [ ] **Phase 3: AI Matching & Assessment**
  - High-recall AI Pre-Screening pipeline.
  - Deep multi-dimensional compatibility assessment (Skills, Experience, Seniority, Location, Language).
  - Match explanation and reasoning interface.
- [ ] **Phase 4: Document Generation & Tailoring**
  - Evidence-grounded CV selection by ID.
  - Grounded cover letter generation with positioning strategies.
  - Static template rendering (`docxtpl` / PDF output) with zero generative distortion.
- [ ] **Phase 5: Automated Asynchronous Pipelines**
  - Redis + Background worker task queues.
  - Scheduled multi-source job fetching & candidate notification service.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
