"""Built-in ``help`` and ``commands`` (always provided by the library unless disabled)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from telegrambot_cli.commands.registry import CommandRegistry, register_decorated, telegram_command


class HelpArgs(BaseModel):
    command: Optional[str] = Field(
        default=None,
        description="Command name to show detailed help for",
    )


def register_builtin_commands(registry: CommandRegistry) -> None:
    @telegram_command(
        name="commands",
        help="List every registered command with a one-line description.",
    )
    def commands_cmd() -> str:
        lines: list[str] = ["Available commands:", ""]
        for spec in registry.all():
            lines.append(f"• `{spec.name}` — {spec.help}")
        lines.extend(["", "Send `help <name>` for usage and arguments."])
        return "\n".join(lines)

    register_decorated(registry, commands_cmd)

    @telegram_command(
        name="help",
        help="Show general help, or detailed help for one command.",
        args_model=HelpArgs,
    )
    def help_cmd(args: HelpArgs) -> str:
        if not args.command:
            return (
                "Message commands (CLI-style):\n\n"
                "• `commands` — list commands\n"
                "• `help <command>` — usage for one command\n\n"
                "You can prefix with `/` (`/help`) or not (`help`)."
            )

        spec = registry.get(args.command)
        if not spec:
            return (
                f"No command named `{args.command}`.\n\n"
                "Try `commands` to see what is available."
            )

        usage = spec.usage(prefix="/")
        parts = [
            spec.name,
            "",
            spec.help,
            "",
            f"Usage: `{usage}`",
        ]

        if spec.args_model is not None:
            parts.extend(["", "Fields:"])
            for fname, finfo in spec.args_model.model_fields.items():
                req = finfo.is_required()
                desc = (finfo.description or "").strip()
                mark = "required" if req else "optional"
                line = f"• `{fname}` ({mark})"
                if desc:
                    line += f" — {desc}"
                parts.append(line)

        return "\n".join(parts)

    register_decorated(registry, help_cmd)
