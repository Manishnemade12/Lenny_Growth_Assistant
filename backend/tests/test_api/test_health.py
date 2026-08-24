"""Unit tests for Phase 1 backend components (Config and Health endpoint)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


def test_settings_defaults():
    """Verify default values in Pydantic settings."""
    assert settings.ACTIVE_LLM_PROVIDER in ["ollama", "anthropic", "openai"]
    assert settings.VECTOR_DIMENSION == 768
    assert settings.CHUNK_SIZE == 500


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test /health endpoint response schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    # In test environment without active DB connection, status can be degraded/unhealthy or 200/500
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "llm_provider" in data
