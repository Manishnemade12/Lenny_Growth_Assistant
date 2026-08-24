"""Agent orchestrator routing incoming messages to appropriate skills and managing response generation."""

import logging
from typing import AsyncGenerator
from uuid import UUID

from app.agent.providers.factory import get_active_provider
from app.agent.skills.artifact_skill import ArtifactSkill
from app.agent.skills.qa_skill import QASkill
from app.agent.skills.ship30_skill import Ship30Skill
from app.db.repositories.message_repo import MessageRepository
from app.db.repositories.session_repo import SessionRepository
from app.rag.retriever import Retriever

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Classifies user intent, selects active skill, executes RAG, and streams response."""

    def __init__(self):
        self.skills = [
            Ship30Skill(),
            ArtifactSkill(),
            QASkill(),  # Default fallback
        ]
        self.retriever = Retriever()

    def classify_intent(self, message: str):
        """Select skill with highest confidence score."""
        best_skill = self.skills[-1]
        best_score = 0.0

        for skill in self.skills:
            score = skill.detect_intent(message)
            if score > best_score:
                best_score = score
                best_skill = skill

        logger.info(f"Routed message to skill: {best_skill.name} (confidence: {best_score})")
        return best_skill

    async def process_message(self, session_id: UUID, message: str, db) -> dict:
        """Process chat message synchronously (non-streaming) and return complete ChatResponse dict."""
        msg_repo = MessageRepository(db)
        await msg_repo.create(session_id=session_id, role="user", content=message)

        history_msgs = await msg_repo.get_by_session(session_id, limit=10)
        history = [{"role": m.role, "content": m.content} for m in history_msgs]

        skill = self.classify_intent(message)
        retrieved_chunks = await self.retriever.search(
            query=message, top_k=skill.retrieval_top_k
        )

        citations = self._extract_citations(retrieved_chunks)
        provider = get_active_provider()
        full_response = ""

        async for text_chunk in skill.execute(
            query=message,
            context=history,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
        ):
            full_response += text_chunk

        saved_msg = await msg_repo.create(
            session_id=session_id,
            role="assistant",
            content=full_response,
            source_citations=citations,
            model_used=f"{provider.name}/{provider.model}",
            token_count=len(full_response.split()),
        )

        return {
            "message_id": saved_msg.id,
            "content": full_response,
            "source_citations": citations,
            "model_used": saved_msg.model_used,
            "token_count": saved_msg.token_count,
            "created_at": saved_msg.created_at,
        }

    async def process_message_stream(
        self, session_id: UUID, message: str, db
    ) -> AsyncGenerator[dict, None]:
        """Process incoming chat query with SSE streaming events."""
        msg_repo = MessageRepository(db)
        await msg_repo.create(session_id=session_id, role="user", content=message)

        history_msgs = await msg_repo.get_by_session(session_id, limit=10)
        history = [{"role": m.role, "content": m.content} for m in history_msgs]

        skill = self.classify_intent(message)
        retrieved_chunks = await self.retriever.search(
            query=message, top_k=skill.retrieval_top_k
        )

        citations = self._extract_citations(retrieved_chunks)
        if citations:
            yield {"type": "source_citations", "citations": citations}

        provider = get_active_provider()
        full_response = ""

        async for text_chunk in skill.execute(
            query=message,
            context=history,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
        ):
            full_response += text_chunk
            yield {"type": "content_delta", "delta": text_chunk}

        await msg_repo.create(
            session_id=session_id,
            role="assistant",
            content=full_response,
            source_citations=citations,
            model_used=f"{provider.name}/{provider.model}",
            token_count=len(full_response.split()),
        )

    def _extract_citations(self, chunks: list[dict]) -> list[dict]:
        return [
            {
                "source_file": c["source_file"],
                "episode_title": c.get("episode_title") or c["source_file"],
                "speaker": c.get("speaker") or "Guest",
                "excerpt": c["content"][:200],
                "similarity_score": round(c.get("score", 0.0), 3),
            }
            for c in chunks[:5]
        ]
