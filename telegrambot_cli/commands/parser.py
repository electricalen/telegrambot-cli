from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Dict, List


class CommandParseError(Exception):
    pass


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    positionals: List[str]
    kwargs: Dict[str, str]


def _split_tokens(text: str) -> List[str]:
    try:
        return shlex.split(text)
    except ValueError as e:
        raise CommandParseError(str(e)) from e


def _normalize_command_name(token: str) -> str:
    return token.lstrip("/").strip()


def parse_command(text: str) -> ParsedCommand:
    """
    Parse message text like:
      - `/echo hello`
      - `echo hello`
      - `cmd --foo bar --flag=true`
      - `cmd foo=bar`

    Rules:
      - First token is the command name (leading `/` stripped).
      - `--key value` becomes kwargs.
      - `key=value` becomes kwargs.
      - Remaining tokens are positional args.
    """
    tokens = _split_tokens(text.strip())
    if not tokens:
        raise CommandParseError("Empty message.")

    name = _normalize_command_name(tokens[0])
    if not name:
        raise CommandParseError("Missing command name.")

    positionals: List[str] = []
    kwargs: Dict[str, str] = {}

    i = 1
    while i < len(tokens):
        tok = tokens[i]

        if tok.startswith("--") and len(tok) > 2:
            key = tok[2:]
            if "=" in key:
                k, v = key.split("=", 1)
                kwargs[k] = v
                i += 1
                continue
            if i + 1 >= len(tokens):
                raise CommandParseError(f"Missing value for --{key}")
            kwargs[key] = tokens[i + 1]
            i += 2
            continue

        if "=" in tok and not tok.startswith("="):
            k, v = tok.split("=", 1)
            if not k:
                raise CommandParseError(f"Invalid token: {tok}")
            kwargs[k] = v
            i += 1
            continue

        positionals.append(tok)
        i += 1

    return ParsedCommand(name=name, positionals=positionals, kwargs=kwargs)
