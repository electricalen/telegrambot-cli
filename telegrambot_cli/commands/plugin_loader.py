from __future__ import annotations

import importlib
import logging
import pkgutil
from types import ModuleType

from telegrambot_cli.commands.registry import CommandRegistry

log = logging.getLogger(__name__)


def load_plugins(package: ModuleType, registry: CommandRegistry) -> None:
    """
    Import every submodule of *package* and call ``register(registry)`` when present.

    Skips module names starting with ``_`` (e.g. ``_template.py``).
    """
    if not hasattr(package, "__path__"):
        raise TypeError(f"{package!r} is not a package")

    for info in sorted(
        pkgutil.iter_modules(package.__path__, f"{package.__name__}."),
        key=lambda item: item.name,
    ):
        short_name = info.name.rpartition(".")[-1]
        if short_name.startswith("_"):
            continue

        module = importlib.import_module(info.name)
        reg = getattr(module, "register", None)
        if not callable(reg):
            log.warning("Plugin %r has no register(registry) — skipped", info.name)
            continue

        reg(registry)
        log.debug("Loaded command plugin %r", info.name)
