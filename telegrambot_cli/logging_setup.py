from __future__ import annotations

import logging

from telegrambot_cli.config import Settings


def setup_logging(settings: Settings) -> None:
    level_str = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
