"""
logger.py — Clean centralized logging for NetWatcher.

Architecture reasoning:
  Every module calls get_logger(__name__) — Python best practice.
  All logging goes through one config point. In production you'd
  add a file handler + JSON formatting for log aggregation (ELK, Loki).
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Return a consistently configured logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:  # Avoid duplicate handlers on re-import
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)

    logger.setLevel(level or logging.WARNING)  # Default silent; CLI raises to INFO
    return logger


def set_global_level(level: int) -> None:
    """Called by CLI to enable verbose logging."""
    logging.getLogger("netwatcher").setLevel(level)
    logging.getLogger("engine").setLevel(level)
    logging.getLogger("data").setLevel(level)
    logging.getLogger("reports").setLevel(level)
