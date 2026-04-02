from __future__ import annotations

from telegram.ext import MessageHandler, filters

from telegrambot_cli.telegram.message_router import on_text_message


def build_handlers() -> list[MessageHandler]:
    return [
        MessageHandler(filters.TEXT, on_text_message),
    ]
