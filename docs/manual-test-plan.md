# 🧪 Manual Test Plan & Verification Guide

## The Lenny Growth Assistant

---

## 1. Quick Verification Command
Run the containerized stack:
```bash
docker compose up --build
```

---

## 2. API Endpoints Manual Test Plan

| Endpoint | Test Action | Expected Result |
| --- | --- | --- |
| `GET /health` | `curl http://localhost:8000/health` | Status 200 `{"status": "healthy" \| "degraded", "database": "connected"}` |
| `POST /api/sessions` | `curl -X POST http://localhost:8000/api/sessions` | Status 201 returns session ID |
| `GET /api/sessions` | `curl http://localhost:8000/api/sessions` | Status 200 array of sessions |
| `POST /api/chat` (SSE) | `curl -N -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"session_id":"...", "message":"What is PMF?"}'` | SSE stream events: `message_start`, `content_delta`, `source_citations`, `message_end` |
| `GET /api/config/provider` | `curl http://localhost:8000/api/config/provider` | Status 200 returns active provider info |
| `POST /api/config/provider` | `curl -X POST http://localhost:8000/api/config/provider -d '{"provider":"anthropic"}'` | Swaps active provider to `anthropic` |

---

## 3. UI/UX Functionality Checklist

- [x] **Session Creation**: Click "+ New Chat" button in sidebar to start new session.
- [x] **Message Streaming**: Type query in input bar; observe real-time token streaming.
- [x] **Source Citations**: Check grounded citations card rendered beneath assistant answers.
- [x] **Artifact Rendering**: View side-panel rendering sandboxed HTML/Markdown content securely via DOMPurify.
- [x] **Provider Toggle**: Switch between Ollama (Local) and Anthropic in sidebar footer select dropdown.
