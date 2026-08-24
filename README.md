# 🚀 The Lenny Growth Assistant

> An AI-powered conversational web application that ingests Lenny's Podcast transcripts to answer complex product & growth questions, generate formatted content, and render interactive artifacts — all grounded in real knowledge.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start (One-Command)](#quick-start-one-command)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [LLM Configuration](#llm-configuration)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**The Lenny Growth Assistant** is a full-stack, AI-powered conversational application built as a Forward Deployment Engineering engagement. It transforms Lenny Rachitsky's podcast transcripts into an intelligent internal assistant that provides:

- **Grounded Q&A** — Answers product management and growth questions strictly from indexed transcripts with source citations
- **Ship 30 for 30 Content Skill** — Generates ~1,250-word essays following Ship 30 for 30 writing principles (strong hook, narrative progression, skimmable formatting, actionable takeaways)
- **Artifact Generation & Viewer** — Creates and renders Markdown/HTML/CSS artifacts inline, similar to Claude Artifacts, with proper sandboxing and sanitization
- **Session Management** — Independent chat sessions with full context persistence
- **Flexible LLM Toggle** — Switch between cloud providers (Anthropic Claude, OpenAI) and local models (Ollama) without code changes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Next.js)                 │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Chat UI  │  │ Session Mgr  │  │  Artifact Viewer (sandbox) │ │
│  └────┬─────┘  └──────┬───────┘  └────────────┬───────────────┘ │
│       │               │                       │                 │
└───────┼───────────────┼───────────────────────┼─────────────────┘
        │               │                       │
        ▼               ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Chat API │  │ Session API  │  │  Artifact API            │   │
│  └────┬─────┘  └──────┬───────┘  └────────────┬─────────────┘   │
│       │               │                       │                 │
│  ┌────▼───────────────▼───────────────────────▼─────────────┐   │
│  │              Agent Layer (Claude Agent SDK)               │   │
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
│  │  RAG / Retrieval Engine  │  │  Structured Logging        │   │
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

For the detailed architecture, see [architecture.md](./architecture.md).

---

## Tech Stack

| Layer          | Technology                                     |
| -------------- | ---------------------------------------------- |
| **Frontend**   | React 18+, TypeScript, Vite                    |
| **Backend**    | Python 3.11+, FastAPI, Uvicorn                 |
| **Agent**      | Anthropic Claude Agent SDK                     |
| **Database**   | PostgreSQL 16+ with pgvector extension         |
| **Embeddings** | Sentence Transformers / Ollama embed models    |
| **Cloud LLM**  | Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o   |
| **Local LLM**  | Ollama (Llama 3.2 / Mistral 7B)               |
| **Deployment** | Docker Compose                                 |
| **Testing**    | Pytest (backend), Vitest (frontend)            |

---

## Prerequisites

- **Docker** & **Docker Compose** v2+ (recommended for one-command startup)
- **Python** 3.11+ (for local development)
- **Node.js** 18+ & npm (for frontend development)
- **Ollama** installed and running (for local LLM demo)
- **PostgreSQL** 16+ with pgvector (or use Docker)
- **Git**

---

## Quick Start (One-Command)

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/lenny-growth-assistant.git
cd lenny-growth-assistant

# 2. Copy environment file and configure
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)

# 3. Ensure Ollama is running with a model pulled
ollama pull llama3.2
ollama pull nomic-embed-text

# 4. Start everything with Docker Compose
docker compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Manual Setup

### Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Ingest transcripts
python -m app.scripts.ingest_transcripts

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
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
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ─── OpenAI (Cloud) ────────────────────────────────────────
OPENAI_API_KEY=sk-...               # Required if ACTIVE_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o

# ─── Ollama (Local) ────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text

# ─── Optional ──────────────────────────────────────────────
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR
CORS_ORIGINS=http://localhost:5173
VECTOR_DIMENSION=768
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

> ⚠️ **Never commit `.env` or any file containing secrets to version control.**

---

## LLM Configuration

### Switching Providers

The LLM provider can be toggled via:

1. **Environment variable**: Set `ACTIVE_LLM_PROVIDER` in `.env`
2. **API endpoint**: `POST /api/config/provider` with `{"provider": "ollama"}`
3. **UI toggle**: Use the settings panel in the frontend sidebar

### Local LLM (Ollama) — Required for Demo

```bash
# Install Ollama (https://ollama.ai)
# Pull required models
ollama pull llama3.2          # Chat model
ollama pull nomic-embed-text  # Embedding model

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Cloud LLM Fallback

If the active provider is unavailable, the system will:
1. Log a warning with structured details
2. Attempt fallback to the next configured provider
3. Return a graceful error if no providers are available

---

## Project Structure

```
lenny-growth-assistant/
├── docker-compose.yml          # One-command orchestration
├── .env.example                # Environment template
├── README.md                   # This file
├── PRD.md                      # Product Requirements Document
├── architecture.md             # System architecture
├── design.md                   # UI/UX design decisions
├── development-phases.md       # Phased development plan
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── main.py             # FastAPI application entry
│   │   ├── config.py           # Settings & environment
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py     # Chat endpoints
│   │   │   │   ├── sessions.py # Session management
│   │   │   │   ├── config.py   # LLM config endpoints
│   │   │   │   ├── artifacts.py# Artifact endpoints
│   │   │   │   └── health.py   # Health check
│   │   │   ├── middleware/     # CORS, logging, error handling
│   │   │   └── deps.py        # Dependency injection
│   │   ├── agent/
│   │   │   ├── orchestrator.py # Agent routing & orchestration
│   │   │   ├── skills/
│   │   │   │   ├── qa_skill.py         # Grounded Q&A
│   │   │   │   ├── ship30_skill.py     # Ship 30 for 30 essays
│   │   │   │   └── artifact_skill.py   # Artifact generation
│   │   │   └── providers/
│   │   │       ├── base.py             # Abstract LLM provider
│   │   │       ├── anthropic.py        # Claude integration
│   │   │       ├── openai.py           # OpenAI integration
│   │   │       └── ollama.py           # Ollama integration
│   │   ├── rag/
│   │   │   ├── embeddings.py   # Embedding generation
│   │   │   ├── retriever.py    # Vector search + reranking
│   │   │   ├── chunker.py      # Text chunking strategies
│   │   │   └── ingestion.py    # Transcript ingestion pipeline
│   │   ├── db/
│   │   │   ├── database.py     # Async DB connection
│   │   │   ├── models.py       # SQLAlchemy models
│   │   │   └── repositories/   # Data access layer
│   │   ├── schemas/            # Pydantic request/response models
│   │   └── scripts/
│   │       └── ingest_transcripts.py
│   └── tests/
│       ├── test_api/
│       ├── test_agent/
│       ├── test_rag/
│       └── conftest.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── InputBar.tsx
│   │   │   │   └── SourceCitation.tsx
│   │   │   ├── Sidebar/
│   │   │   │   ├── SessionList.tsx
│   │   │   │   └── SettingsPanel.tsx
│   │   │   ├── Artifacts/
│   │   │   │   ├── ArtifactViewer.tsx
│   │   │   │   └── ArtifactSandbox.tsx
│   │   │   └── common/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   └── styles/
│   └── tests/
│
├── data/
│   └── transcripts/            # Lenny's Podcast transcripts
│
├── agent-transcripts/          # Coding agent logs (sanitized)
│
└── docs/
    ├── manual-test-plan.md
    └── troubleshooting.md
```

---

## API Documentation

Once the server is running, visit **http://localhost:8000/docs** for the interactive Swagger UI.

### Key Endpoints

| Method | Endpoint                        | Description                        |
| ------ | ------------------------------- | ---------------------------------- |
| GET    | `/health`                       | System health check                |
| POST   | `/api/sessions`                 | Create a new chat session          |
| GET    | `/api/sessions`                 | List all sessions                  |
| GET    | `/api/sessions/{id}`            | Get session with messages          |
| DELETE | `/api/sessions/{id}`            | Delete a session                   |
| POST   | `/api/chat`                     | Send a message (SSE streaming)     |
| POST   | `/api/chat/{id}/ship30`         | Generate Ship 30 for 30 essay      |
| POST   | `/api/artifacts`                | Generate an artifact               |
| GET    | `/api/artifacts/{id}`           | Retrieve a rendered artifact       |
| GET    | `/api/config/provider`          | Get current LLM provider           |
| POST   | `/api/config/provider`          | Switch LLM provider                |

---

## Testing

### Automated Tests

```bash
# Backend tests
cd backend
pytest -v --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm run test
```

### Manual Test Plan

See [docs/manual-test-plan.md](./docs/manual-test-plan.md) for the complete manual test plan covering:
- Session creation and persistence
- Grounded Q&A with source citations
- Ship 30 for 30 essay generation
- Artifact rendering and sandboxing
- LLM provider switching
- Error handling and edge cases

---

## Troubleshooting

### Common Issues

| Issue | Solution |
| ----- | -------- |
| Ollama connection refused | Ensure Ollama is running: `ollama serve` |
| Database connection failed | Check `DATABASE_URL` and PostgreSQL status |
| Missing API key error | Verify `.env` has the correct key for active provider |
| Embeddings dimension mismatch | Ensure `VECTOR_DIMENSION` matches your embed model |
| Docker build fails | Try `docker compose build --no-cache` |
| Slow responses with Ollama | Use a smaller quantized model (e.g., `llama3.2:3b`) |

For detailed troubleshooting, see [docs/troubleshooting.md](./docs/troubleshooting.md).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is created as part of a Forward Deployed Engineer take-home assignment.
