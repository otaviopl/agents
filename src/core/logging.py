from __future__ import annotations

import logging
from typing import Optional


def setup_logging(level: str = "INFO", *, to_file: Optional[str] = None) -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler()]
    if to_file:
        handlers.append(logging.FileHandler(to_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

