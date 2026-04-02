from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegrambot_cli.commands.registry import CommandRegistry
from telegrambot_cli.commands.router import dispatch_message_text

log = logging.getLogger(__name__)


async def on_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Owner-only message entrypoint; routes text into the command framework."""
    if update.effective_user is None or update.effective_chat is None:
        return
    message = update.effective_message
    if message is None or message.text is None:
        return

    owner_ids: set[int] = context.application.bot_data["owner_ids"]
    if update.effective_user.id not in owner_ids:
        return

    known_chat_ids: set[int] = context.application.bot_data["known_owner_chat_ids"]
    known_chat_ids.add(update.effective_chat.id)

    registry: CommandRegistry = context.application.bot_data["command_registry"]
    result = dispatch_message_text(registry=registry, text=message.text, usage_prefix="/")
    await message.reply_text(result.text)
