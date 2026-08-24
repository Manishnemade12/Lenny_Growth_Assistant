# 🧪 Manual Test Plan & Evaluator Handoff Guide

## The Lenny Growth Assistant

---

## 1. Quick Verification (One-Command Docker Compose)

To verify the complete stack with a single command:

```bash
# 1. Clone repository and set up env
git clone https://github.com/Manishnemade12/Lenny_Growth_Assistant.git
cd Lenny_Growth_Assistant
cp .env.example .env

# 2. Build and launch with Docker Compose
docker compose up --build
```

Access Points:
- **Frontend UI**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 2. Comprehensive Test Matrix

### Test Case 1: Grounded Q&A with Source Citations
- **Action**: Type `"What does Lenny say about Product-Market Fit?"` in the chat input bar.
- **Expected Result**:
  - SSE real-time token streaming begins immediately.
  - Collapsible **"📚 Grounded Podcast Sources"** accordion appears beneath response with 5 cited podcast guests (e.g. Rahul Vohra, Amol Avasare).
  - Collapsible **"⚡ Run Details & Assistant Activity"** panel displays `QASkill (Grounded RAG)` routing.

### Test Case 2: Ship 30 for 30 Content Skill
- **Action**: Click the prompt suggestion badge or type `"Write a Ship 30 for 30 essay on growth loops"`.
- **Expected Result**:
  - `Ship30Skill` intent detected with high confidence (0.90).
  - ~1,250 word atomic essay generated following 1/3/1 structure, bold emphasis, and actionable takeaways grounded in transcripts.

### Test Case 3: Artifact Generation & Sandboxed Side-Panel Viewer
- **Action**: Type `"Create an HTML artifact summarizing PMF metrics"` or click `"📄 View Artifact"` on any assistant message.
- **Expected Result**:
  - Side-panel viewer opens beside the chat window.
  - HTML content renders inside a sandboxed `<iframe>` (`sandbox="allow-same-origin"`) sanitized via `DOMPurify`.
  - Artifact Toolbar allows toggling between **👁️ Rendered** view and **📝 Raw Source**, copying text, or downloading the file.

### Test Case 4: LLM Provider Toggle (Ollama vs Cloud)
- **Action**: In the sidebar footer, switch **LLM Provider** dropdown between:
  - `Ollama (Local Default)`
  - `Anthropic Claude 3.5`
  - `OpenAI GPT-4o`
- **Expected Result**:
  - Active provider badge updates instantly (`🟢 ollama`, `🟢 anthropic`, or `🟢 openai`).
  - Next message routes to selected provider.

### Test Case 5: Session Management & Persistence
- **Action**: Click `+ New Chat`, send messages, refresh page (F5).
- **Expected Result**:
  - Chat history and session list persist intact from PostgreSQL.
  - Delete button (`×`) removes session cleanly.

### Test Case 6: Edge Case & Error Resilience
- **Action**: Attempt query when Ollama is offline or when API key is missing.
- **Expected Result**:
  - System gracefully catches error, logs structured JSON alert, and displays user-friendly fallback error message without crashing server.

---

## 3. API Test Plan

| Endpoint | Method | Payload / Params | Expected Status | Expected Output |
| --- | --- | --- | --- | --- |
| `/health` | GET | None | 200 OK | `{"status": "healthy", "database": "connected"}` |
| `/api/sessions` | POST | `{"title": "New Chat"}` | 201 Created | Session object with UUID |
| `/api/sessions` | GET | None | 200 OK | Array of active chat sessions |
| `/api/chat` | POST | `{"session_id": "...", "message": "...", "stream": true}` | 200 OK | SSE stream: `source_citations`, `content_delta`, `message_end` |
| `/api/config/provider` | GET | None | 200 OK | `{"active_provider": "ollama", "active_model": "llama3.2"}` |
| `/api/config/provider` | POST | `{"provider": "anthropic"}` | 200 OK | Swaps active provider to `anthropic` |
