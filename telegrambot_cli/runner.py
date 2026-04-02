from __future__ import annotations

import importlib
import logging
from collections.abc import Callable, Sequence
from types import ModuleType

from telegram import Update
from telegram.ext import Application

from telegrambot_cli.commands.catalog import build_registry
from telegrambot_cli.commands.registry import CommandRegistry
from telegrambot_cli.config import Settings, load_settings
from telegrambot_cli.logging_setup import setup_logging
from telegrambot_cli.monitoring.jobs import schedule_jobs
from telegrambot_cli.telegram.handlers import build_handlers

log = logging.getLogger(__name__)


def run_bot(
    *,
    settings: Settings | None = None,
    register_commands: Callable[[CommandRegistry], None] | None = None,
    plugin_package: str | ModuleType | None = None,
    pre_import_modules: Sequence[str] = (),
    include_builtin_commands: bool = True,
) -> None:
    """
    Start the bot: load optional monitor modules, build settings and registry, poll Telegram.

    Parameters
    ----------
    register_commands
        Optional callback ``def register_commands(registry): ...`` for extra commands.
    plugin_package
        Importable package name or module object; every submodule with ``register(registry)``
        is loaded (skip ``_*``).
    pre_import_modules
        Module names to import before scheduling (for ``@register_monitor`` side effects).
    include_builtin_commands
        If False, omit library ``help`` / ``commands`` (unusual).
    """
    for name in pre_import_modules:
        importlib.import_module(name)

    s = settings or load_settings()
    setup_logging(s)

    registry = build_registry(
        register_commands=register_commands,
        plugin_package=plugin_package,
        include_builtins=include_builtin_commands,
    )

    application = Application.builder().token(s.bot_token).build()
    application.bot_data["settings"] = s
    application.bot_data["owner_ids"] = set(s.owner_id_list)
    application.bot_data["known_owner_chat_ids"] = set()
    application.bot_data["command_registry"] = registry

    for h in build_handlers():
        application.add_handler(h)

    schedule_jobs(application)
    log.info("Starting PTB long polling. owner_ids=%s", s.owner_id_list)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
