"""Grounded QA Skill answering queries strictly using Lenny's Podcast transcript context."""

from typing import AsyncGenerator
from app.agent.providers.base import BaseLLMProvider
from app.agent.skills.base_skill import BaseSkill


class QASkill(BaseSkill):
    """Answers product management and growth questions grounded in podcast transcript context."""

    @property
    def name(self) -> str:
        return "qa_skill"

    @property
    def description(self) -> str:
        return "Grounded Q&A using Lenny's Podcast transcripts"

    @property
    def retrieval_top_k(self) -> int:
        return 5

    @property
    def system_prompt(self) -> str:
        return (
            "You are 'The Lenny Growth Assistant', an expert on product management and growth strategy.\n"
            "Your knowledge comes exclusively from Lenny Rachitsky's podcast transcripts.\n\n"
            "RULES:\n"
            "1. ONLY answer based on the provided transcript context. Never make up information.\n"
            "2. If the context does not contain relevant info, say: 'I don't have enough information from Lenny's transcripts to answer this.'\n"
            "3. Cite specific speakers and episodes when referencing insights.\n"
            "4. Be structured, skimmable, and actionable."
        )

    def detect_intent(self, message: str) -> float:
        return 0.3  # Base fallback score

    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider: BaseLLMProvider,
    ) -> AsyncGenerator[str, None]:
        formatted_context = self._format_chunks(retrieved_chunks)
        messages = []

        for msg in context[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        user_content = (
            f"Based on the following transcript excerpts, answer the question.\n\n"
            f"TRANSCRIPT EXCERPTS:\n{formatted_context}\n\n"
            f"QUESTION: {query}"
        )
        messages.append({"role": "user", "content": user_content})

        async for chunk in provider.generate(
            messages=messages,
            system_prompt=self.system_prompt,
        ):
            yield chunk

    def _format_chunks(self, chunks: list[dict]) -> str:
        if not chunks:
            return "No transcript excerpts found."
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            title = chunk.get("episode_title") or chunk.get("source_file")
            speaker = chunk.get("speaker") or "Guest"
            formatted.append(f"[{i}] Episode: {title} (Speaker: {speaker})\nContent: {chunk['content']}\n")
        return "\n---\n".join(formatted)
