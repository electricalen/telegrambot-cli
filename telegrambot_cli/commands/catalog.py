from __future__ import annotations

import importlib
from collections.abc import Callable
from types import ModuleType

from telegrambot_cli.commands.builtins import register_builtin_commands
from telegrambot_cli.commands.plugin_loader import load_plugins
from telegrambot_cli.commands.registry import CommandRegistry


def build_registry(
    *,
    register_commands: Callable[[CommandRegistry], None] | None = None,
    plugin_package: str | ModuleType | None = None,
    include_builtins: bool = True,
) -> CommandRegistry:
    """
    Assemble a :class:`CommandRegistry`.

    Order:

    1. Built-in ``help`` / ``commands`` (if ``include_builtins``).
    2. All plugins under ``plugin_package`` (each submodule with ``register(registry)``).
    3. Optional ``register_commands(registry)`` callback (e.g. extra inline commands).
    """
    registry = CommandRegistry()
    if include_builtins:
        register_builtin_commands(registry)
    if plugin_package is not None:
        pkg = importlib.import_module(plugin_package) if isinstance(plugin_package, str) else plugin_package
        load_plugins(pkg, registry)
    if register_commands is not None:
        register_commands(registry)
    return registry
