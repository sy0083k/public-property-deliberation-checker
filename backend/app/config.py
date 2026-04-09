from __future__ import annotations

import os

from pydantic import BaseModel, Field


DEFAULT_CORS_ALLOW_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def _parse_csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default

    items = [item.strip() for item in raw.split(",") if item.strip()]
    return items or default


class Settings(BaseModel):
    app_name: str = "Public Property Deliberation Eligibility Checker"
    db_url: str = "sqlite:///./diagnostic.db"
    cors_allow_origins: list[str] = Field(default_factory=lambda: list(DEFAULT_CORS_ALLOW_ORIGINS))


settings = Settings(
    app_name=os.getenv("APP_NAME", "Public Property Deliberation Eligibility Checker"),
    db_url=os.getenv("DB_URL", "sqlite:///./diagnostic.db"),
    cors_allow_origins=_parse_csv_env("CORS_ALLOW_ORIGINS", DEFAULT_CORS_ALLOW_ORIGINS),
)
