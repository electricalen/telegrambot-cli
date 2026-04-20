from __future__ import annotations

import argparse
from collections.abc import Sequence

from telegrambot_cli import __version__
from telegrambot_cli.runner import run_bot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telegrambot-cli",
        description="Run the telegrambot-cli bot using settings from the environment or .env.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for `python -m telegrambot_cli` (built-in commands only)."""
    build_parser().parse_args(argv)
    run_bot()


if __name__ == "__main__":
    main()
