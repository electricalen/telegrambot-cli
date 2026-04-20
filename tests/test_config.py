from __future__ import annotations

from pathlib import Path

import pytest

from telegrambot_cli.config import Settings, load_settings


def test_settings_normalize_owner_ids_from_list() -> None:
    settings = Settings(
        owner_ids=[123, "456"],
        bot_token="token",
    )

    assert settings.owner_ids == "123,456"
    assert settings.owner_id_list == [123, 456]


def test_settings_reject_empty_owner_ids() -> None:
    with pytest.raises(ValueError, match="at least one Telegram user ID"):
        Settings(owner_ids=" , ", bot_token="token")


def test_load_settings_uses_explicit_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TELEGRAM_BOT_TOKEN=secret\nTELEGRAM_OWNER_IDS=1,2\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file)

    assert settings.bot_token == "secret"
    assert settings.owner_id_list == [1, 2]
