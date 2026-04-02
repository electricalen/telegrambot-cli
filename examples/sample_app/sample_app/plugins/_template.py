"""
Template for a new command — not loaded (filename starts with ``_``).

Copy to ``my_command.py`` and implement ``register(registry)``.
"""

from __future__ import annotations

from telegrambot_cli import CommandRegistry, register_decorated, telegram_command


def register(registry: CommandRegistry) -> None:
    @telegram_command(
        name="example",
        help="Template — rename and customize.",
    )
    def example_cmd() -> str:
        return "This plugin is not loaded until you copy it to a file without leading underscore."

    register_decorated(registry, example_cmd)
