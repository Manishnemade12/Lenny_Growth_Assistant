# 🚀 The Lenny Growth Assistant

> A full-stack, AI-powered conversational web application that ingests 50+ Lenny's Podcast transcripts to answer product & growth queries with verifiable citations, generate structured Ship 30 for 30 essays, and render dynamic interactive artifacts in a secure sandbox.

---

## 📋 Table of Contents

- [Overview](#overview)
- [📖 Documentation & Specification Guide](#-documentation--specification-guide)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start (One-Command Docker Compose)](#quick-start-one-command-docker-compose)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Deliverables & Evaluation Checklist](#deliverables--evaluation-checklist)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Troubleshooting](#troubleshooting)

---

## Overview

**The Lenny Growth Assistant** is built as a comprehensive solution for the Forward Deployed Engineer take-home assessment. It transforms raw, unstructured transcript data from Lenny Rachitsky's podcast into an intelligent, grounded internal assistant for Product Managers, Growth Leads, and Startup Operators.

### Key Features & Capabilities

- **Grounded Q&A Engine (RAG)**: Answers complex product management and growth strategy questions strictly grounded in indexed podcast transcripts, providing verifiable source citations (episode title, timestamp/line reference, exact quote).
- **Ship 30 for 30 Content Skill**: Automatically generates ~1,250-word, high-converting essays adhering to Ship 30 for 30 principles (strong hook, 1/3/1 sentence flow, skimmable subheadings, actionable takeaways).
- **Interactive Artifact Viewer**: Generates and renders Markdown, HTML, SVG, and web artifacts inline with client-side DOMPurify sanitization and iframe sandboxing (`sandbox="allow-same-origin"`).
- **Multi-Provider LLM Router**: Seamlessly switch between Cloud Providers (Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o) and Local Models (Ollama `llama3.2` + `nomic-embed-text`) via configuration without changing code.
- **Session & History Persistence**: Full chat history and artifact state tracking backed by PostgreSQL, with REST APIs and Zustand frontend state synchronization.

---

## 📖 Documentation & Specification Guide

This repository contains dedicated, detailed documentation covering every aspect of the project's requirements, design, implementation, and operations. Below is a structured guide to what each file contains:

| Document | Purpose & Key Contents |
| :--- | :--- |
| 📄 **[PRD.md](./PRD.md)** | **Product Requirements Document**: Covers the Forward Deployment Discovery Brief, target user personas (PMs, Growth Leads), Jobs-to-be-Done (JTBD), functional capabilities, success metrics, assumptions, risk matrix, and phase-by-phase acceptance criteria. |
| 🏗️ **[architecture.md](./architecture.md)** | **System Architecture & Specifications**: Details the 3-tier architecture, system component breakdown, database schema (PostgreSQL + `pgvector`), API specs (`/api/chat`, `/api/sessions`, `/api/artifacts`, `/api/config`), LLM provider abstraction layer, RAG indexing pipeline, and security model. |
| 🧪 **[TDD.md](./TDD.md)** | **Technical Design Document**: Contains low-level implementation details, FastAPI application structure, async database connection management (`asyncpg`), Pydantic validation schemas, custom skill routing logic, SSE streaming handler, and logging pipelines. |
| 🎨 **[design.md](./design.md)** | **UI/UX Design Specifications**: Outlines the UI design philosophy (Clarity Over Cleverness, Grounded Trust), full CSS design system (color tokens, typography, spacing), component specs (Chat UI, Sidebar, Artifact Drawer, Citation Modal), micro-interactions, and accessibility rules. |
| 📦 **[development-phases.md](./development-phases.md)** | **Phased Build Plan**: Defines the sequential 6-phase roadmap (Foundation, RAG Engine, Agent Skill Router, Frontend Chat UI, Artifact System, Polish & Docker Deployment) with task breakdowns, estimates, and explicit criteria for completion. |
| 📏 **[CONVENTIONS.md](./CONVENTIONS.md)** | **Development Guidelines & Coding Rules**: Rules governing code structure, backend async practices, strict TypeScript usage, standardized error schemas, structured JSON logging, security standards, and commit message formats. |
| 🤖 **[AGENTS.md](./AGENTS.md)** | **AI Coding Agent Instructions**: Concise rulebook for automated coding agents detailing mandatory reference docs, tech stack restrictions, forbidden packages, naming conventions, and fallback procedures. |
| 🔒 **[docs/artifact-security.md](./docs/artifact-security.md)** | **Artifact Security Specification**: Explains the security architecture for dynamic code rendering, including HTML sanitization with DOMPurify and iframe isolation to prevent XSS attacks. |
| 🧪 **[docs/manual-test-plan.md](./docs/manual-test-plan.md)** | **Manual QA & Verification Plan**: Step-by-step test matrix for verifying Grounded Q&A, Ship 30 essay generation, model switching, session persistence, and UI responsiveness. |
| 🔧 **[docs/troubleshooting.md](./docs/troubleshooting.md)** | **Operational & Setup Troubleshooting**: Step-by-step resolution guide for Docker Compose setup, database connections, Ollama local model integration, and common runtime errors. |
| 📝 **[agent-transcripts/execution_log.md](./agent-transcripts/execution_log.md)** | **Agent Execution Log**: Auditable record of implementation steps, automated build actions, and validation milestones across development phases. |

---

## Architecture

The system uses a modular 3-tier architecture built around an async Python backend, a modern React frontend, and a PostgreSQL database with vector search capabilities.

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 18 + Vite + Zustand)"]
        UI[Chat Window]
        SM[Session Sidebar]
        AV[Sandboxed Artifact Viewer]
    end

    subgraph Backend ["Backend (FastAPI Async)"]
        API[API Routes & Middleware]
        Router[Agent Orchestrator & Intent Router]
        
        subgraph Skills ["Agent Skills"]
            QA[QA Grounded Retrieval Skill]
            Ship30[Ship 30 for 30 Essay Skill]
            ArtSkill[Artifact Generation Skill]
        end

        LLM[LLM Provider Adapter]
        RAG[RAG & Vector Retrieval Engine]
        Log[Structured JSON Logger]
    end

    subgraph External ["LLM Engine Providers"]
        Anthropic[Anthropic Claude 3.5 Sonnet]
        OpenAI[OpenAI GPT-4o]
        Ollama[Ollama Local Llama 3.2]
    end

    subgraph Storage ["Database Layer (PostgreSQL 16)"]
        DB[(Sessions, Messages & pgvector Chunks)]
    end

    UI <-->|HTTP / SSE Stream| API
    SM <-->|REST API| API
    AV <-->|REST API| API

    API --> Router
    Router --> QA & Ship30 & ArtSkill
    QA --> RAG
    RAG <-->|Vector Search| DB
    
    QA & Ship30 & ArtSkill --> LLM
    LLM <--> Anthropic & OpenAI & Ollama
    
    API <-->|SQLAlchemy Async| DB
```

For a deep dive into schemas, data flows, and API endpoints, see [architecture.md](./architecture.md).

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18+, TypeScript (Strict), Vite, Zustand, Vanilla CSS |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2 |
| **Database & Vectors** | PostgreSQL 16+ with `pgvector` extension |
| **Agent Orchestration** | Custom Agent Orchestrator & Skill Router |
| **Cloud LLMs** | Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o |
| **Local LLM** | Ollama (`llama3.2` + `nomic-embed-text`) |
| **Security & Isolation** | DOMPurify (HTML Sanitization), Sandboxed Iframes (`sandbox="allow-same-origin"`) |
| **Containerization** | Docker & Docker Compose |
| **Testing** | Pytest & pytest-asyncio (Backend), Vitest (Frontend) |

---

## Prerequisites

- **Docker & Docker Compose v2+** (Recommended for 1-command startup)
- **Python 3.11+** (For local non-Docker backend setup)
- **Node.js 18+ & npm** (For local non-Docker frontend setup)
- **Ollama** (Required only if evaluating local LLM mode)

---

## Quick Start (One-Command Docker Compose)

To launch the full stack (Frontend, Backend API, PostgreSQL + pgvector):

```bash
# 1. Clone the repository
git clone https://github.com/Manishnemade12/Lenny_Growth_Assistant.git
cd Lenny_Growth_Assistant

# 2. Copy environment variable template
cp .env.example .env

# 3. Pull local models (Optional: only needed if using Ollama provider)
ollama pull llama3.2
ollama pull nomic-embed-text

# 4. Launch the application stack
docker compose up --build
```

### Application Endpoints
- 🌐 **Frontend UI**: [http://localhost:5173](http://localhost:5173)
- ⚙️ **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **OpenAPI (Swagger) Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **System Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Manual Setup (Non-Docker)

### 1. Database
Ensure PostgreSQL 16+ with the `pgvector` extension is running locally and a database named `lenny_assistant` is created.

### 2. Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Linux/Mac: source venv/bin/activate
# On Windows: .\venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Run database migrations and transcript ingestion
alembic upgrade head
python -m app.scripts.ingest_transcripts

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

---

## Environment Variables

Configuration is managed via `.env` in the project root:

```env
# ─── Database ──────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant
SECRET_KEY=your-secret-key-change-in-production

# ─── Active LLM Provider Selection ─────────────────────────────
# Options: anthropic | openai | ollama
ACTIVE_LLM_PROVIDER=ollama

# ─── Anthropic Claude (Cloud) ──────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ─── OpenAI (Cloud) ────────────────────────────────────────────
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# ─── Ollama (Local) ────────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## Project Structure

```
.
├── AGENTS.md                  # Rules and constraints for AI coding agents
├── CONVENTIONS.md             # Code standards, formatting, and design guidelines
├── PRD.md                     # Product Requirements Document
├── README.md                  # Project overview & quick start guide
├── TDD.md                     # Technical Design Document
├── architecture.md            # System architecture and API specifications
├── design.md                  # UI/UX design specifications & design system
├── development-phases.md      # Phased implementation roadmap
├── docker-compose.yml         # Container configuration for local deployment
├── .env.example               # Template for environment configuration
├── agent-transcripts/         # Logs of execution and phase builds
├── backend/                   # FastAPI Backend
│   ├── alembic/               # Database migration scripts
│   ├── app/
│   │   ├── api/               # Routes, middleware & error handling
│   │   ├── agent/             # Intent classifier, skills & LLM providers
│   │   ├── db/                # Database models & async engine
│   │   ├── rag/               # Transcript chunking & vector retrieval
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── scripts/           # Transcript ingestion utilities
│   │   ├── main.py            # FastAPI entry point & lifecycle hooks
│   │   └── config.py          # Pydantic settings management
│   ├── tests/                 # Pytest test suite
│   └── requirements.txt       # Python dependencies
├── data/                      # Raw podcast transcript files
├── docs/                      # Supplemental project documentation
│   ├── artifact-security.md   # Security model & iframe sandboxing docs
│   ├── manual-test-plan.md    # QA manual testing checklist
│   └── troubleshooting.md     # Troubleshooting guide
└── frontend/                  # React + Vite Frontend
    ├── src/
    │   ├── api/               # API client & SSE streaming reader
    │   ├── components/        # React components (Chat, Sidebar, Artifacts)
    │   ├── hooks/             # Custom React hooks
    │   ├── store/             # Zustand global state store
    │   ├── styles/            # Vanilla CSS design tokens & stylesheets
    │   └── types/             # TypeScript interfaces & types
    ├── package.json           # Frontend dependencies
    └── vite.config.ts         # Vite build configuration
```

---

## Deliverables & Evaluation Checklist

<<<<<<< HEAD
| # | Deliverable | Repository Path | Status |
| :--- | :--- | :--- | :--- |
| **1** | **Public GitHub Repository** | `https://github.com/Manishnemade12/Lenny_Growth_Assistant.git` | ✅ Live |
| **2** | **Product Requirements Document** | [PRD.md](./PRD.md) | ✅ Verified |
| **3** | **System Architecture Document** | [architecture.md](./architecture.md) | ✅ Verified |
| **4** | **Technical Design Document** | [TDD.md](./TDD.md) | ✅ Verified |
| **5** | **UI/UX Design Specifications** | [design.md](./design.md) | ✅ Verified |
| **6** | **Development Roadmap & Phases** | [development-phases.md](./development-phases.md) | ✅ Verified |
| **7** | **Code Guidelines & Rules** | [CONVENTIONS.md](./CONVENTIONS.md) & [AGENTS.md](./AGENTS.md) | ✅ Verified |
| **8** | **Agent Transcripts** | [agent-transcripts/execution_log.md](./agent-transcripts/execution_log.md) | ✅ Verified |
| **9** | **Automated & Manual Test Suites** | [backend/tests/](./backend/tests/) & [docs/manual-test-plan.md](./docs/manual-test-plan.md) | ✅ Verified |
| **10**| **Security & Operational Guides** | [docs/artifact-security.md](./docs/artifact-security.md) & [docs/troubleshooting.md](./docs/troubleshooting.md) | ✅ Verified |

### Demo Video Instructions
For evaluating the demo video:
1. Review the problem statement in [PRD.md Section 1](./PRD.md).
2. Showcase **Grounded Q&A** with verifiable transcript citations.
3. Demonstrate generating a **Ship 30 for 30 essay** and viewing dynamic **Artifacts**.
4. Show live LLM provider switching to **local Ollama**.
5. Discuss key trade-offs between vector retrieval latency and cloud LLM latency/costs.

---

## Testing & Quality Assurance

### Backend Automated Tests
```bash
cd backend
pytest -v
```

### Frontend Typecheck & Unit Tests
```bash
cd frontend
npm run typecheck
npm run test
```

### Manual QA Plan
Refer to [docs/manual-test-plan.md](./docs/manual-test-plan.md) for step-by-step test execution scenarios covering streaming, citations, artifact security sandboxing, and edge cases.
=======
| # | Deliverable | Location in Repo | Status |
| --- | --- | --- | --- |
| **1** | **Public GitHub Repository** | `https://github.com/Manishnemade12/Lenny_Growth_Assistant.git` | 
| **2** | **README.md** | [README.md](./README.md) |
| **3** | **PRD.md** | [PRD.md](./PRD.md) ||
| **4** | **design.md** | [design.md](./design.md) | 
| **5** | **architecture.md** | [architecture.md](./architecture.md) | 
| **6** | **Agent Transcripts** | [agent-transcripts/execution_log.md](./agent-transcripts/execution_log.md) | 
| **7** | **Tests & Test Plan** | [backend/tests/](./backend/tests/) & [docs/manual-test-plan.md](./docs/manual-test-plan.md) | 
>>>>>>> df34b4a8463644608dbc048492dbe0a9f999462a

---

## Troubleshooting

<<<<<<< HEAD
Refer to [docs/troubleshooting.md](./docs/troubleshooting.md) for operational support, Docker startup fixes, PostgreSQL vector issues, and Ollama integration details.
=======
See [docs/troubleshooting.md](./docs/troubleshooting.md) for detailed operational troubleshooting covering Docker Compose, Supabase PgBouncer, Ollama local model, and artifact security isolation.

---

>>>>>>> df34b4a8463644608dbc048492dbe0a9f999462a
