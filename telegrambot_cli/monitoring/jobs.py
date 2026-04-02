from __future__ import annotations

import logging

from telegram.ext import Application, ContextTypes

from telegrambot_cli.config import Settings
from telegrambot_cli.monitoring import monitors

log = logging.getLogger(__name__)


def schedule_jobs(application: Application) -> None:
    settings: Settings = application.bot_data["settings"]
    if settings.heartbeat_enabled:
        application.job_queue.run_repeating(
            callback=_heartbeat_job,
            interval=max(5, settings.heartbeat_interval_sec),
            first=5,
            name="heartbeat",
        )

    if monitors.monitor_count() > 0:
        application.job_queue.run_repeating(
            callback=monitors.run_registered_monitors,
            interval=max(10, settings.monitor_interval_sec),
            first=10,
            name="custom_monitors",
        )


async def _heartbeat_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    owner_ids: set[int] = context.application.bot_data["owner_ids"]
    known_chat_ids: set[int] = context.application.bot_data["known_owner_chat_ids"]

    targets: set[int] = set(known_chat_ids) if known_chat_ids else set(owner_ids)
    text = settings.heartbeat_message

    for chat_id in targets:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception:
            log.exception("Failed to send heartbeat to chat_id=%s", chat_id)
