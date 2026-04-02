from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings from a ``.env`` file and the process environment.
    Environment variables override the file.

    Default env file: ``Path.cwd() / ".env"`` (override with ``TELEGRAM_ENV_FILE`` or
    ``load_settings(env_file=...)``).
    """

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
        extra="ignore",
        env_file_encoding="utf-8",
    )

    owner_ids: str = Field(
        ...,
        description="Comma-separated Telegram user IDs allowed to use the bot",
    )

    bot_token: str = Field(..., description="Bot token from BotFather")

    polling_timeout_sec: int = 30

    heartbeat_enabled: bool = True
    heartbeat_interval_sec: int = 900
    heartbeat_message: str = "Heartbeat"

    monitor_interval_sec: int = 120

    log_level: str = "INFO"

    @field_validator("owner_ids", mode="before")
    @classmethod
    def normalize_owner_ids(cls, v: object) -> str:
        if isinstance(v, list):
            return ",".join(str(int(x)) for x in v)
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            return v.strip()
        raise ValueError("owner_ids must be a comma-separated string, int, or list")

    @computed_field
    @property
    def owner_id_list(self) -> List[int]:
        return [int(p.strip()) for p in self.owner_ids.split(",") if p.strip()]


def load_settings(*, env_file: Path | None = None) -> Settings:
    """
    Load settings. If ``env_file`` is omitted, uses ``TELEGRAM_ENV_FILE`` when set,
    otherwise ``Path.cwd() / ".env"``.
    """
    if env_file is not None:
        return Settings(
            _env_file=env_file.expanduser(),
            _env_file_encoding="utf-8",
        )
    path = os.environ.get("TELEGRAM_ENV_FILE")
    if path:
        return Settings(
            _env_file=Path(path).expanduser(),
            _env_file_encoding="utf-8",
        )
    return Settings(
        _env_file=Path.cwd() / ".env",
        _env_file_encoding="utf-8",
    )
