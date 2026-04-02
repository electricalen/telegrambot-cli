from __future__ import annotations

from telegrambot_cli.runner import run_bot


def main() -> None:
    """Entry point for `python -m telegrambot_cli` (built-in commands only)."""
    run_bot()


if __name__ == "__main__":
    main()
