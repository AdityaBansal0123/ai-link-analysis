import os
from typing import Literal, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "AI-Powered Website Link Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 4000

    # LLM Settings
    LLM_PROVIDER: Literal["gemini", "openai", "anthropic", "mock"] = "gemini"
    
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"

    # Scraping & Security
    REQUEST_TIMEOUT_SECONDS: float = 15.0
    MAX_REDIRECTS: int = 5
    MAX_CONTENT_LENGTH: int = 25000  # Characters for LLM context optimization
    ALLOW_MOCK_FALLBACK: bool = True  # If no key set, smoothly use heuristic mock

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on", "debug", "dev")
        return False

    def get_effective_provider(self) -> str:
        """Determines the effective provider based on configured API keys."""
        if self.LLM_PROVIDER == "gemini" and self.GEMINI_API_KEY:
            return "gemini"
        elif self.LLM_PROVIDER == "openai" and self.OPENAI_API_KEY:
            return "openai"
        elif self.LLM_PROVIDER == "anthropic" and self.ANTHROPIC_API_KEY:
            return "anthropic"
        elif self.LLM_PROVIDER == "mock":
            return "mock"
        
        # Auto-detect if LLM_PROVIDER key is missing but another is available
        if self.GEMINI_API_KEY:
            return "gemini"
        if self.OPENAI_API_KEY:
            return "openai"
        if self.ANTHROPIC_API_KEY:
            return "anthropic"
            
        if self.ALLOW_MOCK_FALLBACK:
            return "mock"
            
        return self.LLM_PROVIDER


settings = Settings()
