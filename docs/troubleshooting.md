# 🛠️ Troubleshooting Guide

## Common Setup & Runtime Issues

### 1. Database Connection Errors (`asyncpg.exceptions` / Connection Refused)
- **Symptom**: `Database connection failed` in FastAPI backend logs.
- **Fix**: Ensure PostgreSQL vector container is running:
  ```bash
  docker compose ps
  ```
  If running locally without Docker, verify local PostgreSQL service is active on port 5432 and `vector` extension is installed.

### 2. Ollama Connection Error / Fallback Vector Mode
- **Symptom**: `Cannot connect to Ollama at http://localhost:11434`.
- **Fix**: Ensure Ollama is installed and running:
  ```bash
  ollama serve
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```
  Note: The backend gracefully falls back to deterministic hash vectors if Ollama is unavailable during dev/testing.

### 3. Frontend Build Errors
- **Symptom**: `tsc -b` type import errors.
- **Fix**: All imports in `src/` use explicit `type` annotations (`import type { ... }`). Run `npm run build` inside `frontend/` to verify.
