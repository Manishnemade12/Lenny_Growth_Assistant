# 📄 Product Requirements Document (PRD)

## The Lenny Growth Assistant

**Version:** 1.0  
**Author:** Forward Deployed Engineer  
**Date:** August 2026  
**Status:** Draft → Ready for Review

---

## 1. Forward Deployment Discovery Brief

### 1.1 User and Problem

**Primary User:** Product managers, growth leads, and startup operators within a product and growth team.

**Job to be Done:** These users frequently need to reference insights from Lenny Rachitsky's podcast — recognized as one of the most authoritative sources on product management, growth strategy, and startup operations. Currently, they must manually search through hundreds of podcast episodes, re-watch or re-read transcripts, and synthesize insights by hand.

**Pain Removed:**
- **Time waste**: Eliminates hours spent manually searching, reading, and cross-referencing transcripts
- **Knowledge loss**: Prevents tribal knowledge from being locked in individuals who "remember that one Lenny episode"
- **Content bottleneck**: Removes the friction of creating high-quality, source-grounded written content for newsletters, internal comms, and social media
- **Prompt engineering burden**: Users don't need to understand models, prompts, or RAG infrastructure — the assistant handles grounding, formatting, and citation automatically

### 1.2 Success Metrics

| Metric | Target | Measurement |
| ------ | ------ | ----------- |
| **Answer Groundedness** | ≥ 90% of answers include verifiable source citations | Automated evaluation: % of responses with `source_citations` field populated |
| **Response Latency (P95)** | < 8s for cloud, < 15s for local Ollama | Server-side timing middleware |
| **Session Retention** | Users return for ≥ 3 sessions per week | Session creation timestamps in PostgreSQL |
| **Content Quality** | Ship 30 for 30 essays score ≥ 4/5 on evaluator rubric | Manual evaluation by reviewer |

### 1.3 Assumptions

> The following assumptions were made because the client brief was incomplete:

1. **Transcript Scope**: We will use the publicly available Lenny's Podcast transcript repository (`ChatPRD/lennys-podcast-transcripts` or the official `LennysNewsletter/lennys-newsletterpodcastdata`). We assume markdown-formatted transcripts are available.
2. **Single-User Mode**: The MVP targets a single team using the tool internally. We do not implement multi-tenant authentication. A simple session-based model is sufficient.
3. **Embedding Model**: For local demo, we use `nomic-embed-text` via Ollama for embeddings. For cloud, we use the provider's embedding API.
4. **No Real-time Ingestion**: Transcripts are ingested in batch during setup. A refresh script can be re-run manually. Live/streaming ingestion is out of scope for v1.
5. **Browser-only Client**: No mobile app. The frontend is a responsive web application.
6. **English Only**: All transcripts and interactions are in English.
7. **Evaluator has Docker**: The evaluator has Docker and Docker Compose available for one-command startup.

### 1.4 Scope Choices

#### ✅ Included

| Feature | Rationale |
| ------- | --------- |
| Grounded conversational Q&A with citations | Core requirement — the primary value proposition |
| Ship 30 for 30 content skill | Core requirement — demonstrates agentic skill system |
| Artifact viewer with sandbox | Core requirement — differentiating UX feature |
| Session management & persistence | Core requirement — multi-session context |
| LLM provider toggle (Cloud + Ollama) | Core requirement — evaluator must see local demo |
| Streaming responses (SSE) | Essential UX — reduces perceived latency |
| Structured logging | Core requirement — operational readiness |
| Docker Compose deployment | Core requirement — one-command startup |
| Health endpoints | Core requirement — operational readiness |

#### ❌ Intentionally Excluded

| Feature | Rationale |
| ------- | --------- |
| User authentication / multi-tenant | Adds complexity without evaluation value; single team use |
| Real-time transcript ingestion | Batch ingestion sufficient for demo; incremental adds complexity |
| Multi-language support | All source content is English |
| Mobile native app | Web responsive is sufficient for evaluation |
| Fine-tuned models | Out of scope for timeline; RAG provides sufficient quality |
| Payment / billing | Not relevant to the engagement |
| Advanced analytics dashboard | Nice-to-have; logging provides sufficient observability |

### 1.5 Risks and Trade-offs

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| **Hallucination** | AI generates plausible but unsourced claims | RAG grounding with explicit source citations; instruct model to say "I don't have enough information" when retrieval confidence is low |
| **Latency (Ollama)** | Local models are significantly slower than cloud | Streaming SSE responses; smaller quantized models; UI loading states |
| **Local Model Quality** | Ollama models produce lower-quality reasoning | Clear UI indicator of active provider; documented trade-offs; cloud fallback |
| **Data Leakage** | Transcript data sent to cloud providers | Document data handling; cloud providers have data processing agreements; local Ollama keeps data on-device |
| **Unsafe Artifact Rendering** | XSS via generated HTML artifacts | Sandbox artifacts in iframe with `sandbox` attribute; CSP headers; DOMPurify sanitization |
| **Cost (Cloud)** | High API usage costs with Claude/OpenAI | Token usage logging; configurable max tokens; Ollama as default |
| **Transcript Coverage** | Public repo may not have all episodes | Document data source limitations; allow manual transcript addition |

---

## 2. User Flows

### 2.1 New Session Flow

```
User opens app
  → Sees welcome screen with "New Chat" button
  → Clicks "New Chat"
  → System creates session in PostgreSQL (session_id, created_at)
  → Chat interface loads with empty message history
  → Input bar is focused and ready
```

### 2.2 Grounded Q&A Flow

```
User types: "What does Lenny say about product-market fit?"
  → Frontend sends POST /api/chat with session_id + message
  → Backend receives message, stores in DB
  → Agent orchestrator routes to QA Skill
  → QA Skill triggers RAG retrieval:
      1. Generate embedding for query
      2. Vector search in pgvector (top-k chunks)
      3. Rerank results for relevance
      4. Construct grounded prompt with retrieved context
  → LLM generates response with citations
  → Response streamed via SSE to frontend
  → Frontend renders message with inline source citations
  → User can click citation to see transcript excerpt
```

### 2.3 Ship 30 for 30 Essay Flow

```
User types: "Write a Ship 30 for 30 essay about growth loops"
  → Agent orchestrator detects Ship 30 intent
  → Routes to Ship 30 for 30 Skill
  → Skill retrieves relevant transcript chunks
  → Applies Ship 30 for 30 writing framework:
      - Strong hook (first line grabs attention)
      - ~1,250 words
      - Headings, bullets, selective bold
      - Narrative progression
      - Specific, actionable takeaway
      - All claims grounded in transcripts
  → Generates formatted essay
  → Streams response to chat
  → User can request artifact version for export
```

### 2.4 Artifact Generation Flow

```
User types: "Create an HTML artifact summarizing the key frameworks"
  → Agent orchestrator routes to Artifact Skill
  → Skill generates Markdown or HTML/CSS based on conversation context
  → Backend stores artifact (id, content, type, session_id)
  → Frontend receives artifact metadata
  → Artifact Viewer panel opens alongside chat
  → HTML rendered in sandboxed iframe
  → Markdown rendered with markdown-it
  → User sees rendered artifact, can copy raw content
```

### 2.5 LLM Provider Switch Flow

```
User opens Settings panel
  → Sees current active provider (e.g., "Ollama - llama3.2")
  → Toggles to "Anthropic Claude"
  → Frontend sends POST /api/config/provider
  → Backend validates provider config (API key exists, service reachable)
  → Updates active provider in memory
  → Returns confirmation
  → UI updates provider badge
  → Next message uses new provider
```

---

## 3. Acceptance Criteria

### 3.1 Grounded Conversational Assistant

- [ ] User can ask product/growth questions and receive answers grounded in Lenny's transcripts
- [ ] Each answer includes at least one source citation (transcript name, episode reference)
- [ ] Follow-up questions maintain session context (references to previous messages)
- [ ] System acknowledges when available material does not support an answer ("I don't have enough information from Lenny's transcripts to answer this")
- [ ] Responses stream in real-time via SSE (not blocked until complete)

### 3.2 Ship 30 for 30 Content Skill

- [ ] User can trigger essay generation via natural language ("write a Ship 30 essay about...")
- [ ] Generated essay is approximately 1,250 words
- [ ] Essay follows Ship 30 for 30 format: hook, narrative progression, headings, bullets, bold emphasis
- [ ] Essay includes a specific, actionable takeaway
- [ ] All claims in the essay are grounded in transcript knowledge base
- [ ] Skill logic is encoded as a structured skill, not a one-off prompt

### 3.3 Artifact Generation & Viewer

- [ ] User can request Markdown or HTML/CSS artifacts from conversation
- [ ] Artifact Viewer opens in a side panel adjacent to chat
- [ ] HTML artifacts render in a sandboxed iframe (no script execution, no navigation)
- [ ] Markdown artifacts render with proper formatting (headings, lists, code blocks)
- [ ] User can copy raw artifact content
- [ ] Artifact isolation strategy is documented

### 3.4 Session Management

- [ ] User can create new chat sessions
- [ ] Each session maintains independent context
- [ ] Previous sessions appear in a sidebar list
- [ ] User can switch between sessions
- [ ] Session data persists across page reloads (stored in PostgreSQL)
- [ ] User can delete sessions

### 3.5 LLM Configuration

- [ ] System supports at least one cloud provider (Anthropic Claude or OpenAI)
- [ ] System supports Ollama for local inference
- [ ] Demo runs using Ollama by default
- [ ] Active provider is visible in the UI
- [ ] Provider can be switched without code changes
- [ ] Fallback behavior is documented and graceful

### 3.6 API Quality

- [ ] All endpoints have clear request/response contracts (Pydantic schemas)
- [ ] Input validation with meaningful error messages
- [ ] Structured error responses (consistent error format)
- [ ] Health endpoint returns system status (DB, LLM provider, retrieval engine)
- [ ] API documentation auto-generated via Swagger/OpenAPI

### 3.7 Operational Readiness

- [ ] One-command startup via Docker Compose
- [ ] `.env.example` with safe defaults and documentation
- [ ] No secrets committed to version control
- [ ] Structured logging (JSON format) for all critical paths
- [ ] Graceful handling: missing API keys, Ollama down, DB connection failure, empty retrieval results, model timeout
- [ ] README with complete setup, run, test, and troubleshooting instructions

---

## 4. Non-Functional Requirements

| Requirement | Specification |
| ----------- | ------------- |
| **Response Time** | P95 < 8s (cloud), P95 < 15s (Ollama) |
| **Concurrency** | Handle 10+ concurrent sessions |
| **Data Persistence** | All sessions and messages survive server restarts |
| **Security** | Artifact sandboxing, input sanitization, no XSS |
| **Accessibility** | WCAG 2.1 AA (keyboard navigation, ARIA labels, contrast) |
| **Browser Support** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| **Responsive** | Desktop (1024px+), Tablet (768px+), Mobile (320px+) |

---

## 5. Implementation Plan Summary

See [development-phases.md](./development-phases.md) for the complete phased breakdown.

| Phase | Focus | Duration |
| ----- | ----- | -------- |
| 1 | Foundation & Infrastructure | 2-3 hours |
| 2 | Knowledge Base & RAG Pipeline | 3-4 hours |
| 3 | Agent Layer & Skills | 3-4 hours |
| 4 | Frontend & Chat UI | 3-4 hours |
| 5 | Artifact System | 2-3 hours |
| 6 | Polish, Testing & Deployment | 2-3 hours |

---

## 6. Open Questions for Evaluator

1. **Transcript Source**: Should we use the official `LennysNewsletter/lennys-newsletterpodcastdata` repository or the community `ChatPRD/lennys-podcast-transcripts`? We default to the community repo for broader coverage.
2. **Embedding Storage**: Is Supabase or Railway preferred for PostgreSQL hosting, or is a local Docker PostgreSQL sufficient for evaluation?
3. **Demo Video Upload**: The assignment requests a YouTube upload — should the demo focus on local Ollama functionality or include cloud LLM comparison?
