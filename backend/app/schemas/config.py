"""Pydantic schemas for LLM provider configuration API.

Defines request/response models for the /api/config endpoints.
"""

from pydantic import BaseModel


class ProviderInfo(BaseModel):
    """Information about an available LLM provider.

    Attributes:
        name: Provider identifier (ollama, anthropic, openai).
        status: Availability status (available, configured, not_configured).
        models: List of available model names.
    """

    name: str
    status: str
    models: list[str]


class ProviderConfigResponse(BaseModel):
    """Response body for GET /api/config/provider.

    Attributes:
        active_provider: Currently active provider name.
        active_model: Currently active model name.
        available_providers: List of all configured providers with status.
    """

    active_provider: str
    active_model: str
    available_providers: list[ProviderInfo]


class ProviderSwitchRequest(BaseModel):
    """Request body for POST /api/config/provider.

    Attributes:
        provider: Target provider name to switch to.
        model: Optional model override for the provider.
    """

    provider: str
    model: str | None = None


class ProviderSwitchResponse(BaseModel):
    """Response body after switching LLM provider.

    Attributes:
        active_provider: Newly active provider name.
        active_model: Newly active model name.
    """

    active_provider: str
    active_model: str
