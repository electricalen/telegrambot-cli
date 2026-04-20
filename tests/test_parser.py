from __future__ import annotations

import pytest

from telegrambot_cli.commands.parser import CommandParseError, parse_command


def test_parse_command_supports_positionals_and_kwargs() -> None:
    parsed = parse_command('/time "America/New_York" format=iso --verbose true')

    assert parsed.name == "time"
    assert parsed.positionals == ["America/New_York"]
    assert parsed.kwargs == {"format": "iso", "verbose": "true"}


def test_parse_command_raises_for_missing_flag_value() -> None:
    with pytest.raises(CommandParseError, match="Missing value for --tz"):
        parse_command("time --tz")
