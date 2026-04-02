"""Example command: echo."""

from __future__ import annotations

from pydantic import BaseModel, Field

from telegrambot_cli import CommandRegistry, register_decorated, telegram_command


class EchoArgs(BaseModel):
    text: str = Field(..., description="Text to echo back")


def register(registry: CommandRegistry) -> None:
    @telegram_command(
        name="echo",
        help="Echo your text back (tests args + positionals).",
        args_model=EchoArgs,
    )
    def echo_cmd(args: EchoArgs) -> str:
        return args.text

    register_decorated(registry, echo_cmd)
