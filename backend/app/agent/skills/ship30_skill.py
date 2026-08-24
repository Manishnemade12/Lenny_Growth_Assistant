"""Ship 30 for 30 essay content generation skill."""

import re
from typing import AsyncGenerator
from app.agent.providers.base import BaseLLMProvider
from app.agent.skills.base_skill import BaseSkill


class Ship30Skill(BaseSkill):
    """Generates structured ~1,250 word atomic essays following Ship 30 for 30 principles."""

    TRIGGER_PATTERNS = [
        r"ship\s*30",
        r"write\s+(an?\s+)?essay",
        r"write\s+(an?\s+)?article",
        r"atomic\s+essay",
    ]

    @property
    def name(self) -> str:
        return "ship30_skill"

    @property
    def description(self) -> str:
        return "Generate Ship 30 for 30 style grounded atomic essays"

    @property
    def retrieval_top_k(self) -> int:
        return 8

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert content writer creating a Ship 30 for 30 style essay grounded in podcast transcripts.\n\n"
            "SHIP 30 FOR 30 WRITING FRAMEWORK:\n"
            "1. Strong Hook (First 2 sentences): Who it is for, what it is about, why read it.\n"
            "2. Structure (~1,250 words total): 1/3/1 sequence with H2 section headings.\n"
            "3. Formatting: Short paragraphs (2-3 sentences), bold key emphasis, bullet points.\n"
            "4. Actionable Takeaway: End with '**The Bottom Line:** [specific action]'\n"
            "5. All claims grounded in provided podcast transcript excerpts."
        )

    def detect_intent(self, message: str) -> float:
        msg_lower = message.lower()
        for pattern in self.TRIGGER_PATTERNS:
            if re.search(pattern, msg_lower):
                return 0.9
        if any(w in msg_lower for w in ["essay", "article", "ship 30"]):
            return 0.6
        return 0.0

    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider: BaseLLMProvider,
    ) -> AsyncGenerator[str, None]:
        formatted_context = self._format_chunks(retrieved_chunks)
        messages = [
            {
                "role": "user",
                "content": (
                    f"Write a Ship 30 for 30 essay about:\n{query}\n\n"
                    f"TRANSCRIPT CONTEXT:\n{formatted_context}"
                ),
            }
        ]

        async for chunk in provider.generate(
            messages=messages,
            system_prompt=self.system_prompt,
            max_tokens=4096,
        ):
            yield chunk

    def _format_chunks(self, chunks: list[dict]) -> str:
        if not chunks:
            return "No transcript excerpts found."
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            title = chunk.get("episode_title") or chunk.get("source_file")
            formatted.append(f"[{i}] Episode: {title}\nContent: {chunk['content']}\n")
        return "\n---\n".join(formatted)
