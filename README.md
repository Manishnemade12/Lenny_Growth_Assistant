# 🚀 The Lenny Growth Assistant

> An AI-powered conversational web application that ingests Lenny's Podcast transcripts to answer complex product & growth questions, generate formatted content, and render interactive artifacts — all grounded in real knowledge.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start (One-Command Docker Compose)](#quick-start-one-command-docker-compose)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [LLM Configuration](#llm-configuration)
- [Project Structure](#project-structure)
- [Deliverables Checklist](#deliverables-checklist)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

**The Lenny Growth Assistant** is a full-stack, AI-powered conversational application built for the Forward Deployed Engineer Take-Home Assessment. It transforms Lenny Rachitsky's podcast transcripts into an intelligent internal assistant that provides:

- **Grounded Q&A** — Answers product management and growth questions strictly from indexed transcripts with verifiable source citations
- **Ship 30 for 30 Content Skill** — Generates ~1,250-word essays following Ship 30 for 30 writing principles (strong hook, 1/3/1 structure, skimmable formatting, actionable takeaways)
- **Artifact Generation & Viewer** — Creates and renders Markdown/HTML/CSS artifacts inline with proper DOMPurify sanitization and `iframe` sandboxing
- **Session Management** — Independent chat sessions with full context persistence stored in PostgreSQL
- **Flexible LLM Toggle** — Switch between cloud providers (Anthropic Claude, OpenAI) and local models (Ollama) without code changes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Chat UI  │  │ Session Mgr  │  │  Artifact Viewer (sandbox) │ │
│  └────┬─────┘  └──────┬───────┘  └────────────┬───────────────┘ │
│       │               │                       │                 │
└───────┼───────────────┼───────────────────────┼─────────────────┘
        │               │                       │
        ▼               ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Chat API │  │ Session API  │  │  Artifact API            │   │
│  └────┬─────┘  └──────┬───────┘  └────────────┬─────────────┘   │
│       │               │                       │                 │
│  ┌────▼───────────────▼───────────────────────▼─────────────┐   │
│  │              Agent Layer (Claude Agent SDK / Router)      │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌───────────────────┐ │   │
│  │  │ QA Skill   │  │ Ship30 Skill │  │ Artifact Skill    │ │   │
│  │  └─────┬──────┘  └──────┬───────┘  └────────┬──────────┘ │   │
│  └────────┼────────────────┼───────────────────┼────────────┘   │
│           │                │                   │                │
│  ┌────────▼────────────────▼───────────────────▼────────────┐   │
│  │            LLM Configuration Layer                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐    │   │
│  │  │ Anthropic │  │  OpenAI  │  │  Ollama (Local)      │    │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────┐  ┌────────────────────────────┐   │
│  │  RAG / Retrieval Engine  │  │  Structured JSON Logging   │   │
│  │  (pgvector + embeddings) │  │  (Observability)           │   │
│  └────────────┬─────────────┘  └────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL + pgvector                        │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Sessions │  │ Messages     │  │  Transcript Embeddings   │   │
│  └──────────┘  └──────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

For the detailed system design, see [architecture.md](./architecture.md).

---

## Tech Stack

| Layer          | Technology                                     |
| -------------- | ---------------------------------------------- |
| **Frontend**   | React 18+, TypeScript (strict), Vite, Zustand  |
| **Backend**    | Python 3.11+, FastAPI, SQLAlchemy 2.0 async    |
| **Agent**      | Custom Agent Orchestrator & Skill Router       |
| **Database**   | PostgreSQL 16+ with pgvector extension         |
| **Knowledge**  | 50+ Lenny Podcast Transcripts                  |
| **Cloud LLM**  | Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o   |
| **Local LLM**  | Ollama (Llama 3.2 / nomic-embed-text)          |
| **Deployment** | Docker Compose                                 |
| **Testing**    | Pytest (backend), Vitest (frontend)            |

---

## Prerequisites

- **Docker** & **Docker Compose** v2+ (recommended for one-command startup)
- **Python** 3.11+ (optional for local non-Docker development)
- **Node.js** 18+ & npm (optional for local non-Docker development)
- **Ollama** installed (for local LLM demo)

---

## Quick Start (One-Command Docker Compose)

To evaluate the entire project with a single command:

```bash
# 1. Clone the repository
git clone https://github.com/Manishnemade12/Lenny_Growth_Assistant.git
cd Lenny_Growth_Assistant

# 2. Copy environment file
cp .env.example .env

# 3. Pull Ollama model (for local model demo)
ollama pull llama3.2

# 4. Launch entire containerized stack
docker compose up --build
```

The application will be available at:
- **Frontend UI**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Manual Setup (Non-Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.ingest_transcripts
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# ─── Required ───────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant
SECRET_KEY=your-secret-key-change-in-production

# ─── LLM Provider (choose one as active) ───────────────────
ACTIVE_LLM_PROVIDER=ollama          # Options: anthropic, openai, ollama

# ─── Anthropic (Cloud) ─────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-...        # Required if ACTIVE_LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# ─── OpenAI (Cloud) ────────────────────────────────────────
OPENAI_API_KEY=sk-...               # Required if ACTIVE_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o

# ─── Ollama (Local) ────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
```

> ⚠️ **Never commit `.env` or any secrets file to version control.**

---

## Deliverables Checklist

| # | Deliverable | Location in Repo | Status |
| --- | --- | --- | --- |
| **1** | **Public GitHub Repository** | `https://github.com/Manishnemade12/Lenny_Growth_Assistant.git` | ✅ Live |
| **2** | **README.md** | [README.md](./README.md) | ✅ Verified |
| **3** | **PRD.md** | [PRD.md](./PRD.md) | ✅ Verified |
| **4** | **design.md** | [design.md](./design.md) | ✅ Verified |
| **5** | **architecture.md** | [architecture.md](./architecture.md) | ✅ Verified |
| **6** | **Agent Transcripts** | [agent-transcripts/execution_log.md](./agent-transcripts/execution_log.md) | ✅ Verified |
| **7** | **Tests & Test Plan** | [backend/tests/](./backend/tests/) & [docs/manual-test-plan.md](./docs/manual-test-plan.md) | ✅ Verified |
| **8** | **Demo Video Instructions** | [See instructions below](#demo-video-instructions) | ✅ Ready |

### Demo Video Instructions
Record a 2–3 minute video explaining:
1. The business problem and discovery brief framing
2. End-to-end product demo showing Grounded Q&A, Ship 30 essay, and Artifact Viewer
3. Local Ollama demonstration
4. Explanation of key technical trade-offs (vector search latency vs cloud LLM costs)
5. Upload to YouTube and submit link via submission form.

---

## Troubleshooting

See [docs/troubleshooting.md](./docs/troubleshooting.md) for detailed operational troubleshooting covering Docker Compose, Supabase PgBouncer, Ollama local model, and artifact security isolation.

---

## License

This project is created as part of the Forward Deployed Engineer Take-Home Assessment.
