from __future__ import annotations

import importlib
import logging
from collections.abc import Callable, Sequence
from types import ModuleType

from telegram import Update
from telegram.ext import Application, ApplicationBuilder

from telegrambot_cli.commands.catalog import build_registry
from telegrambot_cli.commands.registry import CommandRegistry
from telegrambot_cli.config import Settings, load_settings
from telegrambot_cli.logging_setup import setup_logging
from telegrambot_cli.monitoring.jobs import schedule_jobs
from telegrambot_cli.telegram.handlers import build_handlers

log = logging.getLogger(__name__)


def build_application(
    *,
    settings: Settings | None = None,
    register_commands: Callable[[CommandRegistry], None] | None = None,
    plugin_package: str | ModuleType | None = None,
    pre_import_modules: Sequence[str] = (),
    include_builtin_commands: bool = True,
    builder: ApplicationBuilder | None = None,
    configure_builder: Callable[[ApplicationBuilder], ApplicationBuilder | None] | None = None,
    configure_logging: bool = True,
    add_default_handlers: bool = True,
    enable_jobs: bool = True,
) -> Application:
    """
    Build a PTB application wired for telegrambot-cli without starting polling.

    This is the preferred public entrypoint when integrating into an existing PTB app,
    custom builder configuration, or a non-polling lifecycle.
    """
    resolved_settings, registry = prepare_runtime(
        settings=settings,
        register_commands=register_commands,
        plugin_package=plugin_package,
        pre_import_modules=pre_import_modules,
        include_builtin_commands=include_builtin_commands,
        configure_logging=configure_logging,
    )

    application_builder = builder or Application.builder()
    application_builder.token(resolved_settings.bot_token)
    if configure_builder is not None:
        maybe_builder = configure_builder(application_builder)
        if maybe_builder is not None:
            application_builder = maybe_builder

    application = application_builder.build()
    configure_application(
        application,
        settings=resolved_settings,
        registry=registry,
        add_default_handlers=add_default_handlers,
        enable_jobs=enable_jobs,
    )
    return application


def prepare_runtime(
    *,
    settings: Settings | None = None,
    register_commands: Callable[[CommandRegistry], None] | None = None,
    plugin_package: str | ModuleType | None = None,
    pre_import_modules: Sequence[str] = (),
    include_builtin_commands: bool = True,
    configure_logging: bool = True,
) -> tuple[Settings, CommandRegistry]:
    """
    Load settings, import monitor modules, and build the command registry.

    Use this when you need the library's settings and registry behavior but want to
    manage the PTB application lifecycle yourself.
    """
    for name in pre_import_modules:
        importlib.import_module(name)

    resolved_settings = settings or load_settings()
    if configure_logging:
        setup_logging(resolved_settings)

    registry = build_registry(
        register_commands=register_commands,
        plugin_package=plugin_package,
        include_builtins=include_builtin_commands,
    )
    return resolved_settings, registry


def configure_application(
    application: Application,
    *,
    settings: Settings,
    registry: CommandRegistry,
    add_default_handlers: bool = True,
    enable_jobs: bool = True,
) -> Application:
    """
    Attach telegrambot-cli state, handlers, and optional jobs to an existing PTB app.

    This enables incremental adoption in applications that already own PTB builder,
    persistence, webhook, or lifecycle configuration.
    """
    application.bot_data["settings"] = settings
    application.bot_data["owner_ids"] = set(settings.owner_id_list)
    application.bot_data.setdefault("known_owner_chat_ids", set())
    application.bot_data["command_registry"] = registry

    if add_default_handlers:
        for handler in build_handlers():
            application.add_handler(handler)

    if enable_jobs:
        schedule_jobs(application)

    return application


def run_bot(
    *,
    settings: Settings | None = None,
    register_commands: Callable[[CommandRegistry], None] | None = None,
    plugin_package: str | ModuleType | None = None,
    pre_import_modules: Sequence[str] = (),
    include_builtin_commands: bool = True,
    builder: ApplicationBuilder | None = None,
    configure_builder: Callable[[ApplicationBuilder], ApplicationBuilder | None] | None = None,
    configure_logging: bool = True,
    add_default_handlers: bool = True,
    enable_jobs: bool = True,
) -> None:
    """
    Build and start the bot with PTB long polling.

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
    builder
        Optional PTB ``ApplicationBuilder`` to customize persistence, request settings,
        rate limiting, and other PTB-level concerns.
    configure_builder
        Optional callback that mutates the PTB builder before ``build()``.
    configure_logging
        If True, configure basic Python logging from ``settings.log_level``.
    add_default_handlers
        If True, attach the owner-only text message handler.
    enable_jobs
        If True, schedule heartbeat and registered monitor jobs.
    """
    application = build_application(
        settings=settings,
        register_commands=register_commands,
        plugin_package=plugin_package,
        pre_import_modules=pre_import_modules,
        include_builtin_commands=include_builtin_commands,
        builder=builder,
        configure_builder=configure_builder,
        configure_logging=configure_logging,
        add_default_handlers=add_default_handlers,
        enable_jobs=enable_jobs,
    )
    s: Settings = application.bot_data["settings"]
    log.info(
        "Starting PTB long polling. owner_ids=%s plugin_package=%s",
        s.owner_id_list,
        plugin_package if isinstance(plugin_package, str) else getattr(plugin_package, "__name__", None),
    )
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        timeout=s.polling_timeout_sec,
    )
