from pathlib import Path

from pydantic import Field
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
    codegen_timeout_s: float = 180.0

    # Validation: apply + go test retries when LLM is enabled (mock path uses 1 attempt).
    validation_max_attempts: int = Field(default=3, ge=1, le=20)

    # Optional GitHub PR (fine-grained or classic PAT with repo scope). If unset, PR step logs skip.
    github_token: str | None = None
    github_repo: str | None = None  # "owner/name" for API + push URL
    # Empty = detect from local repo (main vs master). Set explicitly if needed.
    github_default_branch: str = ""


settings = Settings()
