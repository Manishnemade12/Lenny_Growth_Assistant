# 🧪 Technical Design Document (TDD)

## The Lenny Growth Assistant

---

## 1. Overview

This document covers the technical implementation details, data flow specifications, error handling strategies, and testing approach for The Lenny Growth Assistant. It complements the [Architecture Document](./architecture.md) with lower-level implementation guidance.

---

## 2. Backend Technical Design

### 2.1 FastAPI Application Structure

#### Entry Point (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db.database import init_db, close_db
from app.api.routes import chat, sessions, artifacts, config, health
from app.api.middleware.logging import StructuredLoggingMiddleware
from app.api.middleware.error_handler import global_exception_handler
from app.agent.providers.factory import initialize_providers
from app.rag.ingestion import verify_knowledge_base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await initialize_providers()
    await verify_knowledge_base()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Lenny Growth Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, global_exception_handler)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(artifacts.router, prefix="/api", tags=["Artifacts"])
app.include_router(config.router, prefix="/api", tags=["Configuration"])
```

#### Configuration (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    
    # LLM Providers
    ACTIVE_LLM_PROVIDER: str = "ollama"  # anthropic | openai | ollama
    
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # RAG Configuration
    VECTOR_DIMENSION: int = 768
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 20
    TOP_K_RERANK: int = 5
    SIMILARITY_THRESHOLD: float = 0.3
    
    # Application
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173"
    MAX_MESSAGE_LENGTH: int = 10000
    MAX_TOKENS: int = 4096
    STREAM_CHUNK_DELAY_MS: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.2 Database Layer

#### Async Database Connection (`app/db/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # Verify connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=settings.LOG_LEVEL == "DEBUG",
)

async_session_factory = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### ORM Models (`app/db/models.py`)

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), default="New Chat")
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    source_citations = Column(JSONB, default=list)
    metadata_ = Column("metadata", JSONB, default=dict)
    model_used = Column(String(100))
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_message_role"),
    )
    
    session = relationship("Session", back_populates="messages")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    title = Column(String(255), default="Untitled Artifact")
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint("type IN ('markdown', 'html')", name="ck_artifact_type"),
    )
    
    session = relationship("Session", back_populates="artifacts")

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file = Column(String(500), nullable=False)
    episode_title = Column(String(500))
    speaker = Column(String(255))
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # pgvector
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

### 2.3 Pydantic Schemas (`app/schemas/`)

```python
# chat.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(..., min_length=1, max_length=10000)
    stream: bool = True

class SourceCitation(BaseModel):
    source_file: str
    episode_title: Optional[str] = None
    speaker: Optional[str] = None
    excerpt: str
    similarity_score: float

class ChatResponse(BaseModel):
    message_id: UUID
    content: str
    source_citations: list[SourceCitation] = []
    model_used: str
    token_count: int
    created_at: datetime

# session.py
class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class SessionResponse(BaseModel):
    id: UUID
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

class SessionDetailResponse(SessionResponse):
    messages: list[ChatResponse] = []
    artifacts: list["ArtifactResponse"] = []

# artifact.py
class ArtifactCreate(BaseModel):
    session_id: UUID
    type: str = Field(..., pattern="^(markdown|html)$")
    prompt: str
    context_message_ids: list[UUID] = []

class ArtifactResponse(BaseModel):
    id: UUID
    type: str
    title: str
    content: str
    created_at: datetime

# common.py
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: str
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str  # healthy | degraded | unhealthy
    database: str
    llm_provider: str
    llm_model: str
    llm_status: str
    retrieval_engine: str
    transcript_count: int
    timestamp: datetime
```

### 2.4 SSE Streaming Implementation

```python
# app/api/routes/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.agent.orchestrator import AgentOrchestrator
from app.db.database import get_db
import json

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db = Depends(get_db),
    orchestrator: AgentOrchestrator = Depends()
):
    if not request.stream:
        # Non-streaming response
        response = await orchestrator.process_message(
            session_id=request.session_id,
            message=request.message,
            db=db
        )
        return response
    
    # SSE streaming response
    async def event_stream():
        try:
            yield f"event: message_start\ndata: {json.dumps({'status': 'started'})}\n\n"
            
            full_content = ""
            async for chunk in orchestrator.process_message_stream(
                session_id=request.session_id,
                message=request.message,
                db=db
            ):
                if chunk["type"] == "content_delta":
                    full_content += chunk["delta"]
                    yield f"event: content_delta\ndata: {json.dumps(chunk)}\n\n"
                elif chunk["type"] == "source_citations":
                    yield f"event: source_citations\ndata: {json.dumps(chunk)}\n\n"
                elif chunk["type"] == "artifact":
                    yield f"event: artifact\ndata: {json.dumps(chunk)}\n\n"
            
            yield f"event: message_end\ndata: {json.dumps({'status': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

---

## 3. Agent Layer Technical Design

### 3.1 Orchestrator Implementation

```python
# app/agent/orchestrator.py
import logging
from typing import AsyncGenerator
from app.agent.skills.qa_skill import QASkill
from app.agent.skills.ship30_skill import Ship30Skill
from app.agent.skills.artifact_skill import ArtifactSkill
from app.agent.providers.factory import get_active_provider
from app.rag.retriever import Retriever
from app.db.repositories.message_repo import MessageRepository
from app.db.repositories.session_repo import SessionRepository

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.skills = [
            Ship30Skill(),      # Check first (more specific)
            ArtifactSkill(),    # Check second
            QASkill(),          # Default fallback
        ]
        self.retriever = Retriever()
    
    async def _classify_intent(self, message: str) -> "BaseSkill":
        """Route message to the most appropriate skill."""
        best_skill = self.skills[-1]  # Default to QA
        best_score = 0.0
        
        for skill in self.skills:
            score = skill.detect_intent(message)
            if score > best_score:
                best_score = score
                best_skill = skill
        
        logger.info(
            "Intent classified",
            extra={
                "skill": best_skill.name,
                "confidence": best_score,
                "message_preview": message[:100]
            }
        )
        return best_skill
    
    async def process_message_stream(
        self,
        session_id,
        message: str,
        db
    ) -> AsyncGenerator[dict, None]:
        """Process a message and yield streaming chunks."""
        # 1. Store user message
        msg_repo = MessageRepository(db)
        await msg_repo.create(session_id=session_id, role="user", content=message)
        
        # 2. Get conversation history
        session_repo = SessionRepository(db)
        history = await session_repo.get_messages(session_id, limit=20)
        
        # 3. Classify intent and select skill
        skill = await self._classify_intent(message)
        
        # 4. Retrieve relevant chunks (RAG)
        retrieved_chunks = await self.retriever.search(
            query=message,
            top_k=skill.retrieval_top_k
        )
        
        # 5. Execute skill with streaming
        provider = get_active_provider()
        full_response = ""
        
        async for chunk in skill.execute(
            query=message,
            context=history,
            retrieved_chunks=retrieved_chunks,
            provider=provider
        ):
            full_response += chunk
            yield {"type": "content_delta", "delta": chunk}
        
        # 6. Extract and yield source citations
        citations = self._extract_citations(retrieved_chunks)
        if citations:
            yield {"type": "source_citations", "citations": citations}
        
        # 7. Store assistant message
        await msg_repo.create(
            session_id=session_id,
            role="assistant",
            content=full_response,
            source_citations=citations,
            model_used=f"{provider.name}/{provider.model}"
        )
    
    def _extract_citations(self, chunks: list[dict]) -> list[dict]:
        """Format retrieved chunks as source citations."""
        return [
            {
                "source_file": chunk["source_file"],
                "episode_title": chunk.get("episode_title", ""),
                "speaker": chunk.get("speaker", ""),
                "excerpt": chunk["content"][:200],
                "similarity_score": chunk["score"]
            }
            for chunk in chunks[:5]
        ]
```

### 3.2 QA Skill Implementation

```python
# app/agent/skills/qa_skill.py
import re
from typing import AsyncGenerator
from app.agent.skills.base_skill import BaseSkill

class QASkill(BaseSkill):
    
    @property
    def name(self) -> str:
        return "qa_skill"
    
    @property
    def description(self) -> str:
        return "Answer product management and growth questions using Lenny's Podcast transcripts"
    
    @property
    def retrieval_top_k(self) -> int:
        return 5
    
    @property
    def system_prompt(self) -> str:
        return """You are "The Lenny Growth Assistant," an expert on product management and growth strategy. 
Your knowledge comes exclusively from Lenny Rachitsky's podcast transcripts.

RULES:
1. ONLY answer based on the provided transcript context. Never make up information.
2. If the context doesn't contain relevant information, say: "I don't have enough information from Lenny's transcripts to answer this question."
3. Always cite the specific episode/guest when referencing information.
4. Maintain conversation context from previous messages.
5. Be specific and actionable in your answers.
6. Use direct quotes when particularly insightful.

FORMAT:
- Use markdown formatting for readability
- Bold key concepts and names
- Use bullet points for lists
- Include source citations at the end in the format: [Source: Episode Title - Guest Name]
"""
    
    def detect_intent(self, message: str) -> float:
        """QA is the default skill — returns a base confidence."""
        return 0.3  # Low base; other skills override if they match
    
    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider
    ) -> AsyncGenerator[str, None]:
        """Execute grounded Q&A with RAG context."""
        # Build context from retrieved chunks
        rag_context = self._format_chunks(retrieved_chunks)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add conversation history
        for msg in context[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current query with RAG context
        messages.append({
            "role": "user",
            "content": f"""Based on the following transcript excerpts, answer the user's question.

TRANSCRIPT CONTEXT:
{rag_context}

USER QUESTION: {query}

Remember: Only use information from the provided transcripts. Cite sources."""
        })
        
        async for chunk in provider.generate(messages=messages, system_prompt=self.system_prompt):
            yield chunk
    
    def _format_chunks(self, chunks: list[dict]) -> str:
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            formatted.append(
                f"[{i}] Episode: {chunk.get('episode_title', 'Unknown')}\n"
                f"Speaker: {chunk.get('speaker', 'Unknown')}\n"
                f"Content: {chunk['content']}\n"
            )
        return "\n---\n".join(formatted)
```

### 3.3 Ship 30 for 30 Skill Implementation

```python
# app/agent/skills/ship30_skill.py
import re
from typing import AsyncGenerator
from app.agent.skills.base_skill import BaseSkill

class Ship30Skill(BaseSkill):
    
    TRIGGER_PATTERNS = [
        r"ship\s*30",
        r"write\s+(an?\s+)?essay",
        r"write\s+(an?\s+)?article",
        r"atomic\s+essay",
        r"content\s+(piece|creation)",
        r"newsletter\s+(post|article)",
    ]
    
    @property
    def name(self) -> str:
        return "ship30_skill"
    
    @property
    def description(self) -> str:
        return "Generate Ship 30 for 30 style essays grounded in Lenny's Podcast transcripts"
    
    @property
    def retrieval_top_k(self) -> int:
        return 8  # More context for longer-form content
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert content writer creating a Ship 30 for 30 style essay.
        
SHIP 30 FOR 30 WRITING FRAMEWORK:
You must follow these principles precisely:

1. HOOK (First 2 sentences):
   - Open with a surprising statistic, counterintuitive insight, or provocative question
   - Answer three questions: WHO is this for? WHAT is this about? WHY should they read it?
   - The hook must create immediate curiosity

2. STRUCTURE (~1,250 words total):
   - Use the 1/3/1 pattern: 1 intro paragraph, 3 body sections, 1 conclusion
   - Each section has a clear heading (H2)
   - Short paragraphs (2-3 sentences max)
   - White space between sections for readability

3. FORMATTING:
   - **Bold** key insights, names, and frameworks
   - Use bullet points for lists (no more than 5 items per list)
   - Include at least 2 direct quotes from the transcripts
   - Use H2 headings for major sections
   - Use H3 headings for sub-points within sections

4. NARRATIVE PROGRESSION:
   - Problem/Observation → Framework/Insight → Evidence → Application → Takeaway
   - Each section builds on the previous one
   - Transitions connect ideas naturally

5. ACTIONABLE TAKEAWAY:
   - End with ONE specific, actionable takeaway
   - Format as: "**The Bottom Line:** [specific action the reader can take tomorrow]"
   - Make it concrete, not vague

6. GROUNDING:
   - Every major claim must reference a specific Lenny's Podcast episode or guest
   - Use format: "As [Guest Name] shared on Lenny's Podcast..."
   - Never invent quotes or attribute claims to guests who didn't make them
   - If you don't have enough source material, say so

IMPORTANT: Generate approximately 1,250 words. Count roughly. The essay should feel substantial but not bloated.
"""
    
    def detect_intent(self, message: str) -> float:
        """Check if the message requests a Ship 30 for 30 essay."""
        message_lower = message.lower()
        for pattern in self.TRIGGER_PATTERNS:
            if re.search(pattern, message_lower):
                return 0.9
        
        # Weaker signals
        if any(word in message_lower for word in ["essay", "article", "write", "blog"]):
            return 0.5
        
        return 0.0
    
    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider
    ) -> AsyncGenerator[str, None]:
        """Generate a Ship 30 for 30 essay."""
        rag_context = self._format_chunks(retrieved_chunks)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""Write a Ship 30 for 30 style essay about the following topic, 
using ONLY information from Lenny's Podcast transcripts provided below.

TOPIC: {query}

TRANSCRIPT CONTEXT:
{rag_context}

Generate a ~1,250 word essay following the Ship 30 for 30 framework exactly.
Include source citations for all major claims."""
            }
        ]
        
        async for chunk in provider.generate(
            messages=messages,
            system_prompt=self.system_prompt,
            max_tokens=4096,
            temperature=0.7
        ):
            yield chunk
```

### 3.4 Ollama Provider Implementation

```python
# app/agent/providers/ollama.py
import httpx
import json
import logging
from typing import AsyncGenerator
from app.agent.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self._model = settings.OLLAMA_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def model(self) -> str:
        return self._model
    
    async def generate(
        self,
        messages: list[dict],
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate response from Ollama, streaming by default."""
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        if data.get("done", False):
                            break
        except httpx.ConnectError:
            logger.error("Failed to connect to Ollama", extra={"url": self.base_url})
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out", extra={"model": self._model})
            raise TimeoutError(f"Ollama model {self._model} timed out after 120s")
    
    async def embed(self, text: str) -> list[float]:
        """Generate embedding using Ollama's embed endpoint."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.embed_model, "input": text},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"][0]
        except httpx.ConnectError:
            raise ConnectionError(f"Cannot connect to Ollama for embeddings at {self.base_url}")
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                return self._model in models or any(self._model in m for m in models)
            return False
        except Exception:
            return False
```

---

## 4. RAG Pipeline Technical Design

### 4.1 Transcript Ingestion

```python
# app/rag/ingestion.py
import os
import logging
from pathlib import Path
from app.rag.chunker import RecursiveCharacterChunker
from app.rag.embeddings import EmbeddingService
from app.db.repositories.transcript_repo import TranscriptRepository
from app.config import settings

logger = logging.getLogger(__name__)

class TranscriptIngester:
    
    def __init__(self, db, embedding_service: EmbeddingService):
        self.db = db
        self.embedder = embedding_service
        self.chunker = RecursiveCharacterChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.repo = TranscriptRepository(db)
    
    async def ingest_directory(self, transcript_dir: str):
        """Ingest all markdown transcripts from a directory."""
        path = Path(transcript_dir)
        transcript_files = list(path.glob("*.md")) + list(path.glob("*.txt"))
        
        logger.info(f"Found {len(transcript_files)} transcript files to ingest")
        
        for file_path in transcript_files:
            await self.ingest_file(file_path)
        
        logger.info("Transcript ingestion complete")
    
    async def ingest_file(self, file_path: Path):
        """Ingest a single transcript file."""
        # Check if already ingested
        existing = await self.repo.get_by_source(str(file_path.name))
        if existing:
            logger.info(f"Skipping already ingested: {file_path.name}")
            return
        
        content = file_path.read_text(encoding="utf-8")
        metadata = self._extract_metadata(file_path.name, content)
        
        # Chunk the content
        chunks = self.chunker.split(content)
        
        logger.info(
            f"Processing {file_path.name}",
            extra={"chunks": len(chunks), "episode": metadata.get("episode_title")}
        )
        
        # Generate embeddings and store
        for i, chunk_text in enumerate(chunks):
            embedding = await self.embedder.embed(chunk_text)
            
            await self.repo.create_chunk(
                source_file=file_path.name,
                episode_title=metadata.get("episode_title"),
                speaker=metadata.get("speaker"),
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                metadata=metadata
            )
    
    def _extract_metadata(self, filename: str, content: str) -> dict:
        """Extract episode metadata from filename and content headers."""
        metadata = {"source_file": filename}
        
        # Try to extract episode title from first heading
        lines = content.split("\n")
        for line in lines[:5]:
            if line.startswith("# "):
                metadata["episode_title"] = line[2:].strip()
                break
        
        # Try to extract from filename
        if "episode_title" not in metadata:
            name = filename.replace(".md", "").replace(".txt", "")
            metadata["episode_title"] = name.replace("-", " ").replace("_", " ").title()
        
        return metadata
```

### 4.2 Chunking Strategy

```python
# app/rag/chunker.py
import re
from typing import List

class RecursiveCharacterChunker:
    """Split text into chunks with configurable size and overlap."""
    
    SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        # Clean the text
        text = self._clean_text(text)
        
        # Split using recursive character approach
        chunks = self._recursive_split(text, self.SEPARATORS)
        
        # Add overlap
        overlapped_chunks = self._add_overlap(chunks)
        
        return overlapped_chunks
    
    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and remove artifacts."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def _recursive_split(self, text: str, separators: list) -> List[str]:
        """Recursively split text using progressively finer separators."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        current_sep = separators[0] if separators else ""
        remaining_seps = separators[1:] if len(separators) > 1 else []
        
        parts = text.split(current_sep)
        current_chunk = ""
        
        for part in parts:
            test_chunk = current_chunk + current_sep + part if current_chunk else part
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                if len(part) > self.chunk_size and remaining_seps:
                    sub_chunks = self._recursive_split(part, remaining_seps)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between consecutive chunks."""
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks
        
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            # Prepend end of previous chunk
            prev_tail = chunks[i-1][-self.chunk_overlap:]
            overlapped.append(prev_tail + " " + chunks[i])
        
        return overlapped
```

### 4.3 Vector Retrieval

```python
# app/rag/retriever.py
import logging
from sqlalchemy import text
from app.rag.embeddings import EmbeddingService
from app.db.database import async_session_factory
from app.config import settings

logger = logging.getLogger(__name__)

class Retriever:
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def search(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> list[dict]:
        """Search for relevant transcript chunks using vector similarity."""
        top_k = top_k or settings.TOP_K_RETRIEVAL
        threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed(query)
        
        # Vector search using pgvector
        async with async_session_factory() as db:
            result = await db.execute(
                text("""
                    SELECT 
                        id, source_file, episode_title, speaker, 
                        chunk_index, content, metadata,
                        1 - (embedding <=> :query_vec::vector) as score
                    FROM transcript_chunks
                    WHERE 1 - (embedding <=> :query_vec::vector) > :threshold
                    ORDER BY embedding <=> :query_vec::vector
                    LIMIT :top_k
                """),
                {
                    "query_vec": str(query_embedding),
                    "threshold": threshold,
                    "top_k": top_k
                }
            )
            
            rows = result.fetchall()
        
        chunks = [
            {
                "id": str(row.id),
                "source_file": row.source_file,
                "episode_title": row.episode_title,
                "speaker": row.speaker,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "score": float(row.score),
                "metadata": row.metadata
            }
            for row in rows
        ]
        
        logger.info(
            "Vector search completed",
            extra={
                "query_preview": query[:100],
                "results": len(chunks),
                "top_score": chunks[0]["score"] if chunks else 0
            }
        )
        
        return chunks
```

---

## 5. Error Handling Strategy

### 5.1 Error Categories

| Category | HTTP Code | Error Code | Example |
| -------- | --------- | ---------- | ------- |
| **Validation** | 422 | `VALIDATION_ERROR` | Invalid session_id format |
| **Not Found** | 404 | `NOT_FOUND` | Session doesn't exist |
| **Provider Error** | 503 | `LLM_UNAVAILABLE` | Ollama not running |
| **Timeout** | 504 | `LLM_TIMEOUT` | Model took too long |
| **Retrieval Empty** | 200 | — | No matching chunks (handled in response) |
| **Database** | 500 | `DATABASE_ERROR` | Connection pool exhausted |
| **Internal** | 500 | `INTERNAL_ERROR` | Unexpected exception |

### 5.2 Global Error Handler

```python
# app/api/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler with structured logging."""
    
    error_mapping = {
        ConnectionError: (503, "LLM_UNAVAILABLE", "LLM provider is unavailable"),
        TimeoutError: (504, "LLM_TIMEOUT", "LLM request timed out"),
        ValueError: (422, "VALIDATION_ERROR", str(exc)),
    }
    
    status_code, error_code, message = error_mapping.get(
        type(exc), 
        (500, "INTERNAL_ERROR", "An unexpected error occurred")
    )
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "error_code": error_code,
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": error_code,
            "detail": str(exc) if status_code != 500 else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
```

### 5.3 Resilience Patterns

```python
# Graceful fallback chain for LLM providers
async def get_response_with_fallback(messages, providers):
    """Try providers in order, falling back on failure."""
    errors = []
    
    for provider in providers:
        try:
            if not await provider.health_check():
                continue
            
            async for chunk in provider.generate(messages):
                yield chunk
            return  # Success
            
        except (ConnectionError, TimeoutError) as e:
            errors.append(f"{provider.name}: {e}")
            logger.warning(f"Provider {provider.name} failed, trying next", extra={"error": str(e)})
            continue
    
    raise ConnectionError(f"All LLM providers failed: {'; '.join(errors)}")
```

---

## 6. Testing Strategy

### 6.1 Test Categories

| Category | Tool | Coverage Target | What is Tested |
| -------- | ---- | --------------- | -------------- |
| **Unit Tests** | pytest | 80%+ | Chunker, skill intent detection, schema validation |
| **Integration Tests** | pytest + httpx | Key flows | API endpoints, DB operations, provider switching |
| **RAG Tests** | pytest | Critical paths | Ingestion, retrieval accuracy, embedding consistency |
| **Frontend Tests** | Vitest + Testing Library | Components | Chat rendering, SSE handling, artifact sandbox |
| **E2E Tests** | Manual | Acceptance criteria | Full user flows per PRD |

### 6.2 Test Structure

```
backend/tests/
├── conftest.py                    # Fixtures: test DB, mock providers
├── test_api/
│   ├── test_health.py             # Health endpoint returns status
│   ├── test_sessions.py           # CRUD operations
│   ├── test_chat.py               # Chat + streaming
│   ├── test_artifacts.py          # Artifact CRUD
│   └── test_config.py             # Provider switching
├── test_agent/
│   ├── test_orchestrator.py       # Intent routing
│   ├── test_qa_skill.py           # QA skill behavior
│   ├── test_ship30_skill.py       # Ship 30 intent detection
│   └── test_artifact_skill.py     # Artifact generation
├── test_rag/
│   ├── test_chunker.py            # Chunking correctness
│   ├── test_retriever.py          # Vector search
│   └── test_ingestion.py          # File processing
└── test_providers/
    ├── test_ollama.py             # Ollama integration
    └── test_provider_fallback.py  # Fallback chain
```

### 6.3 Key Test Fixtures

```python
# conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import engine, Base

@pytest.fixture
async def test_db():
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider that returns predictable responses."""
    class MockProvider:
        name = "mock"
        model = "mock-model"
        
        async def generate(self, messages, **kwargs):
            yield "This is a mock response about product management."
        
        async def embed(self, text):
            return [0.1] * 768
        
        async def health_check(self):
            return True
    
    return MockProvider()
```

---

## 7. Performance Considerations

| Concern | Strategy |
| ------- | -------- |
| **Database connection exhaustion** | Connection pooling (10 base, 20 overflow) with `pool_pre_ping` |
| **Slow embedding generation** | Batch embedding during ingestion; single embed for queries |
| **Large context windows** | Limit conversation history to last 20 messages |
| **Vector search latency** | IVFFlat index on embedding column; limit to top-20 retrieval |
| **SSE backpressure** | Disable nginx buffering; `X-Accel-Buffering: no` |
| **Memory (Ollama)** | Use quantized models (3B/7B); `num_predict` cap |
| **Frontend rendering** | Virtualized message list for long conversations |
| **Concurrent sessions** | Async throughout; no blocking I/O |

---

## 8. Migration Strategy

Using Alembic for PostgreSQL schema migrations:

```bash
# Initialize alembic
alembic init alembic

# Generate migration from models
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

Migration files are committed to version control to ensure reproducible schema setup.
