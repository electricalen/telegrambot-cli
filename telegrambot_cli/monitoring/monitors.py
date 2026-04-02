from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from telegram.ext import ContextTypes

log = logging.getLogger(__name__)

MonitorCallback = Callable[[ContextTypes.DEFAULT_TYPE], Awaitable[None]]

_monitors: list[MonitorCallback] = []


def register_monitor(fn: MonitorCallback) -> MonitorCallback:
    """
    Register an async callback to run on a schedule (see ``schedule_jobs``).

    Ensure the defining module is imported before ``run_bot`` (e.g. via
    ``pre_import_modules``).
    """

    _monitors.append(fn)
    return fn


def monitor_count() -> int:
    return len(_monitors)


async def run_registered_monitors(context: ContextTypes.DEFAULT_TYPE) -> None:
    for fn in _monitors:
        try:
            await fn(context)
        except Exception:
            log.exception("Monitor callback failed: %s", getattr(fn, "__name__", repr(fn)))
