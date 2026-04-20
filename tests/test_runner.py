from __future__ import annotations

from telegram.ext import Application

from telegrambot_cli import build_application, configure_application, prepare_runtime
from telegrambot_cli.commands.registry import CommandRegistry
from telegrambot_cli.config import Settings


def test_prepare_runtime_builds_registry_without_logging_side_effects() -> None:
    settings, registry = prepare_runtime(
        settings=Settings(owner_ids="1", bot_token="token"),
        configure_logging=False,
    )

    assert settings.owner_id_list == [1]
    assert registry.get("help") is not None
    assert registry.get("commands") is not None


def test_configure_application_attaches_state_without_jobs() -> None:
    application = Application.builder().token("token").build()
    settings = Settings(owner_ids="1,2", bot_token="token")
    registry = CommandRegistry()

    configure_application(
        application,
        settings=settings,
        registry=registry,
        add_default_handlers=False,
        enable_jobs=False,
    )

    assert application.bot_data["settings"] is settings
    assert application.bot_data["owner_ids"] == {1, 2}
    assert application.bot_data["known_owner_chat_ids"] == set()
    assert application.bot_data["command_registry"] is registry


def test_build_application_returns_configured_application() -> None:
    application = build_application(
        settings=Settings(owner_ids="7", bot_token="token"),
        include_builtin_commands=False,
        configure_logging=False,
        add_default_handlers=False,
        enable_jobs=False,
    )

    assert application.bot_data["settings"].owner_id_list == [7]
    assert application.bot_data["command_registry"].all() == []
