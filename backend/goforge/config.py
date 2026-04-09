from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "sandbox-repo"


def _default_db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "goforge.db"


def _default_clone_cache_root() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "clones"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GOFORGE_",
        env_file=".env",
        extra="ignore",
    )

    repo_root: Path = _default_repo_root()
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Persist run snapshots to SQLite (survives process restarts; GET /api/run/{id} works after restart).
    persistence_enabled: bool = True
    db_path: Path = Field(default_factory=_default_db_path)

    # Optional OpenAI-compatible API (Planner agent). If unset, planner uses mock output.
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    planner_timeout_s: float = 120.0
    codegen_timeout_s: float = 180.0

    # RAG: embed chunks and retrieve top-k (requires same API key as LLM calls).
    rag_enabled: bool = True
    openai_embedding_model: str = "text-embedding-3-small"
    rag_top_k: int = Field(default=5, ge=1, le=20)
    rag_chunk_chars: int = Field(default=1800, ge=400, le=12_000)
    rag_max_chunks_embed: int = Field(default=120, ge=8, le=400)

    # Validation: apply + go test retries when LLM is enabled (mock path uses 1 attempt).
    validation_max_attempts: int = Field(default=3, ge=1, le=20)

    # Optional: clone a remote HTTPS repo for a run (POST /api/run { "repo_url": "https://..." }).
    remote_clone_enabled: bool = True
    clone_cache_root: Path = Field(default_factory=_default_clone_cache_root)
    clone_timeout_s: float = Field(default=600.0, ge=30.0, le=7200.0)
    # Comma-separated hostnames (empty = github.com, gitlab.com, bitbucket.org, codeberg.org).
    remote_allowed_hosts: str = ""

    # Optional GitHub PR (fine-grained or classic PAT with repo scope). If unset, PR step logs skip.
    github_token: str | None = None
    github_repo: str | None = None  # "owner/name" for API + push URL
    # Empty = detect from local repo (main vs master). Set explicitly if needed.
    github_default_branch: str = ""


settings = Settings()
