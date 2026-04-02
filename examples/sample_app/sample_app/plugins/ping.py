"""Example command: ping."""

from __future__ import annotations

from telegrambot_cli import CommandRegistry, register_decorated, telegram_command


def register(registry: CommandRegistry) -> None:
    @telegram_command(
        name="ping",
        help="Health check.",
    )
    def ping_cmd() -> str:
        return "pong"

    register_decorated(registry, ping_cmd)
