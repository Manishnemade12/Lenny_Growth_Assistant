"""Application configuration loaded from environment variables.

Uses Pydantic Settings to validate and type-check all configuration.
All settings have safe defaults for local development with Ollama.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized application configuration.

    All values can be overridden via environment variables or a .env file.
    Required variables will cause a startup error if missing.
    """

    # ─── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant"

    # ─── Security ──────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"

    # ─── LLM Providers ─────────────────────────────────────────
    ACTIVE_LLM_PROVIDER: str = "ollama"  # anthropic | openai | ollama

    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # ─── RAG Configuration ─────────────────────────────────────
    VECTOR_DIMENSION: int = 768
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 20
    TOP_K_RERANK: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    # ─── Application ───────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173"
    MAX_MESSAGE_LENGTH: int = 10000
    MAX_TOKENS: int = 4096
    STREAM_CHUNK_DELAY_MS: int = 0

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()
