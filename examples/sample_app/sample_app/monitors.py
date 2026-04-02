"""
Optional proactive monitors: use ``@register_monitor`` from ``telegrambot_cli``.

This module is listed in ``pre_import_modules`` so decorators run at startup.
"""

from __future__ import annotations

# Example (uncomment and implement):
#
# from telegrambot_cli import register_monitor
#
# @register_monitor
# async def my_periodic_check(context):
#     settings = context.application.bot_data["settings"]
#     owner_ids = context.application.bot_data["owner_ids"]
#     for chat_id in owner_ids:
#         await context.bot.send_message(chat_id=chat_id, text="Monitor tick ...")
