# 🛠️ Operational Troubleshooting & Handoff Guide

## The Lenny Growth Assistant

---

## 1. Container & Deployment Issues

### Docker Compose Startup Failures
- **Symptom**: `docker compose up --build` fails or container exits immediately.
- **Fix**: Rebuild images without cached layers:
  ```bash
  docker compose down -v
  docker compose build --no-cache
  docker compose up
  ```

### Supabase PgBouncer Connection Error (`asyncpg.exceptions.InvalidSQLStatementNameError`)
- **Symptom**: `prepared statement "..." does not exist` when connecting to Supabase pooler (port 6543).
- **Fix**: The backend automatically detects Supabase PgBouncer URLs and sets `prepared_statement_cache_size=0`. Ensure `DATABASE_URL` in `.env` contains your Supabase pooler connection string.

---

## 2. Local Model & RAG Pipeline Issues

### Ollama Model Offline (`[Ollama local model 'llama3.2' is offline]`)
- **Symptom**: Local LLM provider returns fallback error message.
- **Fix**: Start Ollama service and pull the required model weights:
  ```bash
  ollama serve
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```
  Alternatively, toggle the LLM provider in the frontend sidebar to **Anthropic Claude 3.5** or **OpenAI GPT-4o**.

### Database Vector Extension Missing on Host
- **Symptom**: `type "vector" does not exist` on plain PostgreSQL installations.
- **Fix**: The system automatically executes Alembic migrations with savepoint detection and provides keyword fallback search if `pgvector` C extension is missing on non-Docker hosts. For full vector similarity search, run via Docker Compose (`pgvector/pgvector:pg16`) or use Supabase PostgreSQL.

---

## 3. Frontend & API Issues

### `/api/sessions 404 Not Found`
- **Symptom**: Frontend dev server returns HTML 404 page for API calls.
- **Fix**: Verify `frontend/vite.config.ts` contains the `/api` proxy definition targeting `http://localhost:8000`. Restart Vite dev server: `npm run dev`.

### Input Bar Textarea Lock
- **Symptom**: Unable to type in the input bar while assistant is processing.
- **Fix**: The textarea does not use `disabled={disabled}` to allow continuous typing. Ensure frontend is running latest code from `origin/main`.

---

## 4. Security & Artifact Rendering Handoff

### Artifact Sandboxing Verification
- **Symptom**: Question regarding security of LLM-generated HTML artifacts.
- **Verification**: All HTML content passes through `DOMPurify.sanitize()` stripping script tags, object/embed tags, and inline event handlers, and is rendered inside an `<iframe>` container constrained by `sandbox="allow-same-origin"`. See [docs/artifact-security.md](./artifact-security.md) for full security documentation.
