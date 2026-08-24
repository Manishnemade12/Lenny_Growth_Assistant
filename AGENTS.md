# AGENTS.md — AI Coding Agent Instructions

> This file configures AI coding assistants working on this project. All AI agents (Claude, Codex, Cursor, etc.) must follow these rules.

---

## Project Identity

- **Project Name**: The Lenny Growth Assistant
- **Type**: Full-stack AI-powered conversational web application
- **Purpose**: Forward Deployed Engineer take-home assignment
- **Due Date**: 25/08/26 EOD
- **Evaluation Focus**: Customer judgment, technical execution, agentic architecture, deployment readiness, code quality, UI/UX, communication

---

## Mandatory References

Before making any code changes, read and adhere to:

1. **[PRD.md](./PRD.md)** — Product requirements, acceptance criteria, user flows
2. **[architecture.md](./architecture.md)** — System design, database schema, API contracts
3. **[TDD.md](./TDD.md)** — Technical implementation details, code patterns
4. **[design.md](./design.md)** — UI/UX principles, color system, component specs
5. **[development-phases.md](./development-phases.md)** — Phased build plan with task breakdown
6. **[CONVENTIONS.md](./CONVENTIONS.md)** — Code style, naming conventions, rules

---

## Core Rules

### Rule 1: Follow the Phase Plan
Development MUST follow the phases in [development-phases.md](./development-phases.md). Complete Phase N before starting Phase N+1. Each phase has explicit acceptance criteria — verify them before moving on.

### Rule 2: Match the Architecture Exactly
The file structure, component boundaries, and data flow in [architecture.md](./architecture.md) are the source of truth. Do not invent new patterns or restructure without explicit approval.

### Rule 3: Use the Correct Tech Stack
- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 async / Alembic / Pydantic v2
- **Frontend**: React 18+ / TypeScript (strict) / Vite / Zustand / Vanilla CSS
- **Database**: PostgreSQL 16 + pgvector
- **LLM**: Ollama (local, default) + Anthropic Claude (cloud)
- **Deploy**: Docker Compose
- **DO NOT** use: Flask, Django, Express, Tailwind CSS, Material UI, shadcn/ui, SQLite, MongoDB, socket.io

### Rule 4: Async Everywhere (Backend)
Every database query, HTTP call, and LLM interaction must use `async/await`. Use `httpx.AsyncClient` (not `requests`). Use `asyncpg` via SQLAlchemy async engine. Never block the event loop.

### Rule 5: Type Everything
- **Python**: Type hints on all function signatures and return types. Use `list[str]` not `List[str]`.
- **TypeScript**: Strict mode. Explicit interfaces for props, state, and API responses. Never use `any`.

### Rule 6: Structured Errors
All API errors must return:
```json
{
  "error": "Human-readable message",
  "code": "ERROR_CODE",
  "detail": "optional context",
  "timestamp": "ISO 8601"
}
```

### Rule 7: Structured Logging
Use Python `logging` module with JSON formatter. Include context (session_id, skill name, provider, latency). Never use `print()`.

### Rule 8: Security First
- Sanitize HTML with DOMPurify before rendering artifacts
- Sandbox iframes with `sandbox="allow-same-origin"` (no `allow-scripts`)
- Never commit `.env` files or API keys
- Use Pydantic validation on all API inputs
- Parameterized queries only (no string concatenation SQL)

### Rule 9: Test Critical Paths
- API endpoint happy paths and error paths
- Skill intent detection (true/false positives)
- RAG chunker edge cases
- Provider fallback behavior
- Use mocks for LLM calls in tests

### Rule 10: Documentation is Code
Every function has docstrings. Every component has JSDoc. Every API endpoint has OpenAPI docs (via FastAPI auto-gen). The README must be accurate and up-to-date at all times.

---

## File Naming Conventions

| Type | Convention | Example |
| ---- | ---------- | ------- |
| Python modules | snake_case | `qa_skill.py`, `transcript_repo.py` |
| Python classes | PascalCase | `QASkill`, `OllamaProvider` |
| Python functions | snake_case | `detect_intent`, `process_message_stream` |
| TypeScript components | PascalCase | `ChatWindow.tsx`, `MessageBubble.tsx` |
| TypeScript hooks | camelCase with `use` prefix | `useChat.ts`, `useSessions.ts` |
| CSS files | kebab-case or component name | `globals.css`, `chat.css` |
| Database tables | snake_case, plural | `sessions`, `messages`, `transcript_chunks` |
| Database columns | snake_case | `session_id`, `created_at`, `source_file` |
| API routes | kebab-case | `/api/sessions`, `/api/config/provider` |
| Environment variables | UPPER_SNAKE_CASE | `DATABASE_URL`, `ACTIVE_LLM_PROVIDER` |

---

## When You're Unsure

1. **Check the PRD** — Does the acceptance criteria address this?
2. **Check the TDD** — Is there a code pattern already defined?
3. **Check CONVENTIONS.md** — Is there a rule about this?
4. **Default to simplicity** — The evaluator must understand your choices quickly
5. **Document your decision** — If you make an assumption, write it down in a comment or the relevant doc

---

## Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, test, refactor, style, chore
Scopes: backend, frontend, db, agent, rag, config, docker
```

Examples:
```
feat(agent): implement Ship 30 for 30 skill with intent detection
fix(rag): handle empty retrieval results gracefully
docs(readme): add Ollama setup instructions
test(api): add session CRUD integration tests
refactor(providers): extract common streaming logic to base class
```
