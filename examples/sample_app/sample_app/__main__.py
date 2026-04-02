from __future__ import annotations

from telegrambot_cli import run_bot


def main() -> None:
    run_bot(
        plugin_package="sample_app.plugins",
        pre_import_modules=("sample_app.monitors",),
    )


if __name__ == "__main__":
    main()
