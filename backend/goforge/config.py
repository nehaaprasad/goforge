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


settings = Settings()
