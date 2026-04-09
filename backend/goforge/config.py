from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "sandbox-repo"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GOFORGE_",
        env_file=".env",
        extra="ignore",
    )

    repo_root: Path = _default_repo_root()
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Optional OpenAI-compatible API (Planner agent). If unset, planner uses mock output.
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    planner_timeout_s: float = 120.0


settings = Settings()
