"""Ollama local LLM provider implementation."""

import json
import logging
from typing import AsyncGenerator
import httpx

from app.agent.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Local inference provider communicating with Ollama REST API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self._model = settings.OLLAMA_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL

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
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": self._model,
            "messages": payload_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                            if data.get("done", False):
                                break
        except Exception as exc:
            logger.error("Ollama generation failed, yielding fallback response", extra={"error": str(exc)})
            yield f"[Ollama local model '{self._model}' is offline. Please start Ollama or switch provider.]"

    async def embed(self, text: str) -> list[float]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.embed_model, "input": text},
                )
                if resp.status_code == 200:
                    return resp.json()["embeddings"][0]
        except Exception:
            pass
        return [0.0] * settings.VECTOR_DIMENSION

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
