"""
Reusable Telegram bot framework: owner-only message CLI + optional JobQueue monitors.

Typical app (see ``examples/sample_app``)::

    from telegrambot_cli import run_bot

    run_bot(
        plugin_package=\"myapp.plugins\",
        pre_import_modules=(\"myapp.monitors\",),
    )
"""

from __future__ import annotations

from telegrambot_cli.commands.catalog import build_registry
from telegrambot_cli.commands.registry import (
    CommandRegistry,
    register_decorated,
    telegram_command,
)
from telegrambot_cli.config import Settings, load_settings
from telegrambot_cli.monitoring.monitors import register_monitor
from telegrambot_cli.runner import run_bot

__all__ = [
    "CommandRegistry",
    "Settings",
    "build_registry",
    "load_settings",
    "register_decorated",
    "register_monitor",
    "run_bot",
    "telegram_command",
]

__version__ = "0.2.0"
