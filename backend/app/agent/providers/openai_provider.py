"""OpenAI cloud LLM provider integration."""

import logging
from typing import AsyncGenerator
import httpx

from app.agent.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Cloud LLM provider for OpenAI GPT models (e.g. gpt-4o)."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self._model = settings.OPENAI_MODEL

    @property
    def name(self) -> str:
        return "openai"

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
        if not self.api_key:
            yield "[OpenAI API Key not configured. Please set OPENAI_API_KEY in .env settings.]"
            return

        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": self._model,
            "messages": payload_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                import json
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                pass
        except Exception as exc:
            logger.error("OpenAI generation failed", extra={"error": str(exc)})
            yield f"[OpenAI Provider Error: {str(exc)}]"

    async def embed(self, text: str) -> list[float]:
        if not self.api_key:
            return [0.0] * settings.VECTOR_DIMENSION

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    json={"model": "text-embedding-3-small", "input": text},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                if res.status_code == 200:
                    return res.json()["data"][0]["embedding"]
        except Exception:
            pass
        return [0.0] * settings.VECTOR_DIMENSION

    async def health_check(self) -> bool:
        return bool(self.api_key)
