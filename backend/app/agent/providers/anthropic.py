"""Anthropic Claude cloud LLM provider implementation."""

import logging
from typing import AsyncGenerator
import anthropic

from app.agent.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Cloud provider integration for Anthropic Claude models."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self._model = settings.ANTHROPIC_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if self.api_key else None

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    async def generate(
        self,
        messages: list[dict],
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        if not self.client or not self.api_key:
            yield "[Anthropic API Key not configured. Please set ANTHROPIC_API_KEY in .env settings.]"
            return

        try:
            formatted_messages = [m for m in messages if m["role"] != "system"]
            async with self.client.messages.stream(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=formatted_messages,
            ) as stream_resp:
                async for text in stream_resp.text_stream:
                    yield text
        except Exception as exc:
            logger.error("Anthropic generation failed", extra={"error": str(exc)})
            yield f"[Anthropic Provider Error: {str(exc)}]"

    async def embed(self, text: str) -> list[float]:
        # Anthropic does not provide vector embedding API, return fallback zeros
        return [0.0] * settings.VECTOR_DIMENSION

    async def health_check(self) -> bool:
        return bool(self.api_key)
