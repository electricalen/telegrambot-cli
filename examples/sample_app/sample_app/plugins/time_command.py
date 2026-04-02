"""Example command: time — current time in a timezone."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from telegrambot_cli import CommandRegistry, register_decorated, telegram_command


class TimeArgs(BaseModel):
    tz: str = Field(default="UTC", description="IANA timezone, e.g. America/New_York")


def register(registry: CommandRegistry) -> None:
    @telegram_command(
        name="time",
        help="Current time in a timezone.",
        args_model=TimeArgs,
    )
    def time_cmd(args: TimeArgs) -> str:
        try:
            tz = ZoneInfo(args.tz)
        except Exception:
            return f"Unknown timezone: {args.tz!r}. Try e.g. `UTC` or `America/New_York`."

        now = datetime.now(timezone.utc).astimezone(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")

    register_decorated(registry, time_cmd)
