from __future__ import annotations

from pydantic import BaseModel, Field

from telegrambot_cli.commands.registry import CommandRegistry, register_decorated, telegram_command
from telegrambot_cli.commands.router import dispatch_message_text


class EchoArgs(BaseModel):
    text: str = Field(..., description="Text to echo back")


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()

    @telegram_command(name="echo", help="Echo text.", args_model=EchoArgs)
    def echo(args: EchoArgs) -> str:
        return args.text.upper()

    @telegram_command(name="ping", help="Health check.")
    def ping() -> str:
        return "pong"

    register_decorated(registry, echo)
    register_decorated(registry, ping)
    return registry


def test_dispatch_message_text_supports_positional_binding() -> None:
    result = dispatch_message_text(
        registry=build_registry(),
        text="echo hello world",
        usage_prefix="/",
    )

    assert result.text == "HELLO WORLD"


def test_dispatch_message_text_reports_validation_errors() -> None:
    result = dispatch_message_text(
        registry=build_registry(),
        text="echo text= extra",
        usage_prefix="/",
    )

    assert "Unexpected positional arguments" in result.text
    assert "Usage: `/echo text=<str>`" in result.text


def test_dispatch_message_text_reports_unknown_command() -> None:
    result = dispatch_message_text(
        registry=build_registry(),
        text="missing",
        usage_prefix="/",
    )

    assert result.text == "Unknown command: `missing`\n\nTry `/commands`"
