"""Artifact generation skill producing clean Markdown or HTML/CSS snippets."""

import re
from typing import AsyncGenerator
from app.agent.providers.base import BaseLLMProvider
from app.agent.skills.base_skill import BaseSkill


class ArtifactSkill(BaseSkill):
    """Generates complete Markdown documents or HTML/CSS components for side-panel rendering."""

    TRIGGER_PATTERNS = [
        r"create\s+(an?\s+)?artifact",
        r"generate\s+(html|markdown|md|code)",
        r"create\s+(an?\s+)?html",
        r"render\s+(an?\s+)?artifact",
    ]

    @property
    def name(self) -> str:
        return "artifact_skill"

    @property
    def description(self) -> str:
        return "Generate standalone Markdown or HTML/CSS artifacts"

    @property
    def retrieval_top_k(self) -> int:
        return 5

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert UI developer and technical document writer.\n"
            "Generate standalone, self-contained Markdown or HTML/CSS documents based on conversation context.\n"
            "For HTML, output valid HTML5 snippets with embedded <style> CSS blocks.\n"
            "Do NOT include external scripts or external remote URLs."
        )

    def detect_intent(self, message: str) -> float:
        msg_lower = message.lower()
        for pattern in self.TRIGGER_PATTERNS:
            if re.search(pattern, msg_lower):
                return 0.85
        return 0.0

    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider: BaseLLMProvider,
    ) -> AsyncGenerator[str, None]:
        messages = [{"role": "user", "content": query}]
        async for chunk in provider.generate(
            messages=messages,
            system_prompt=self.system_prompt,
        ):
            yield chunk
