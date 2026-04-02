from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, ValidationError

from telegrambot_cli.commands.parser import CommandParseError, parse_command
from telegrambot_cli.commands.registry import CommandRegistry


class CommandDispatchError(Exception):
    def __init__(self, message: str, *, usage: Optional[str] = None) -> None:
        super().__init__(message)
        self.usage = usage


@dataclass(frozen=True)
class CommandResult:
    text: str


def dispatch_message_text(
    *,
    registry: CommandRegistry,
    text: str,
    usage_prefix: str = "",
) -> CommandResult:
    """
    Parse and run a command from plain message text.

    Returns a user-friendly response text.
    """
    try:
        parsed = parse_command(text)
    except CommandParseError as e:
        return CommandResult(text=f"Parse error: {e}\n\nTry `{usage_prefix}help`")

    spec = registry.get(parsed.name)
    if not spec:
        return CommandResult(text=f"Unknown command: `{parsed.name}`\n\nTry `{usage_prefix}commands`")

    args_obj: Optional[BaseModel] = None
    if spec.args_model is not None:
        try:
            data = dict(parsed.kwargs)
            if parsed.positionals:
                first_field = next(iter(spec.args_model.model_fields.keys()), None)
                if first_field and first_field not in data:
                    data[first_field] = " ".join(parsed.positionals)
                else:
                    return CommandResult(
                        text=(
                            f"Unexpected positional arguments after fields were already set: "
                            f"{' '.join(parsed.positionals)!r}\n\n"
                            f"Usage: `{spec.usage(prefix=usage_prefix)}`"
                        )
                    )
            args_obj = spec.args_model(**data)
        except ValidationError as e:
            return CommandResult(
                text=_format_validation_error(
                    command_name=spec.name,
                    help_text=spec.help,
                    usage=spec.usage(prefix=usage_prefix),
                    error=e,
                )
            )

    try:
        if args_obj is None:
            out = spec.handler()
        else:
            out = spec.handler(args_obj)
    except Exception as e:
        return CommandResult(text=f"Command failed: `{spec.name}`\nError: {e}")

    return CommandResult(text=out or "")


def _format_validation_error(
    *,
    command_name: str,
    help_text: str,
    usage: str,
    error: ValidationError,
) -> str:
    lines: list[str] = [f"Invalid arguments for `{command_name}`.", "", f"Usage: `{usage}`"]
    if help_text:
        lines.extend(["", help_text])
    lines.append("")
    for err in error.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        lines.append(f"- {loc}: {msg}")
    return "\n".join(lines).strip()
