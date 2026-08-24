"""Provider factory for managing LLM provider lifecycle, switching, and fallback execution."""

import logging
from app.agent.providers.anthropic import AnthropicProvider
from app.agent.providers.base import BaseLLMProvider
from app.agent.providers.ollama import OllamaProvider
from app.agent.providers.openai_provider import OpenAIProvider
from app.config import settings

logger = logging.getLogger(__name__)

_active_provider_instance: BaseLLMProvider | None = None
_registered_providers: dict[str, BaseLLMProvider] = {}


async def initialize_providers():
    """Instantiate and register available cloud and local LLM providers."""
    global _active_provider_instance, _registered_providers

    _registered_providers["ollama"] = OllamaProvider()
    _registered_providers["anthropic"] = AnthropicProvider()
    _registered_providers["openai"] = OpenAIProvider()

    set_active_provider(settings.ACTIVE_LLM_PROVIDER)
    logger.info(f"Initialized providers. Active: {get_active_provider().name}")


def get_active_provider() -> BaseLLMProvider:
    """Return currently active provider instance."""
    global _active_provider_instance
    if not _active_provider_instance:
        _active_provider_instance = _registered_providers.get("ollama") or OllamaProvider()
    return _active_provider_instance


def set_active_provider(name: str) -> BaseLLMProvider:
    """Toggle active provider by name."""
    global _active_provider_instance
    if name in _registered_providers:
        _active_provider_instance = _registered_providers[name]
    else:
        logger.warning(f"Unknown provider '{name}', falling back to Ollama")
        _active_provider_instance = _registered_providers.get("ollama") or OllamaProvider()
    return _active_provider_instance


def list_providers_info() -> list[dict]:
    """List availability and configuration details for all registered providers."""
    info = []
    for name, prov in _registered_providers.items():
        status = "configured"
        if name == "ollama":
            status = "available"
        elif name == "anthropic" and not settings.ANTHROPIC_API_KEY:
            status = "not_configured"
        elif name == "openai" and not settings.OPENAI_API_KEY:
            status = "not_configured"

        info.append({
            "name": name,
            "status": status,
            "models": [prov.model],
        })
    return info
