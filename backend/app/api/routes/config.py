"""FastAPI Provider Configuration API routes."""

from fastapi import APIRouter
from app.agent.providers.factory import (
    get_active_provider,
    list_providers_info,
    set_active_provider,
)
from app.schemas.config import (
    ProviderConfigResponse,
    ProviderSwitchRequest,
    ProviderSwitchResponse,
)

router = APIRouter()


@router.get("/config/provider", response_model=ProviderConfigResponse)
async def get_provider_config():
    """Get active provider and available providers list."""
    active = get_active_provider()
    return ProviderConfigResponse(
        active_provider=active.name,
        active_model=active.model,
        available_providers=list_providers_info(),
    )


@router.post("/config/provider", response_model=ProviderSwitchResponse)
async def switch_provider(payload: ProviderSwitchRequest):
    """Switch active LLM provider."""
    new_provider = set_active_provider(payload.provider)
    return ProviderSwitchResponse(
        active_provider=new_provider.name,
        active_model=new_provider.model,
    )
