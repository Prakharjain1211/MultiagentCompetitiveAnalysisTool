"""
Logging configuration using Loguru.

Provides a single `setup_logger()` function that configures:
    - Console sink: colorized, INFO level, human-readable format.
    - File sink: structured DEBUG-level logging with rotation and retention.

Usage:
    from src.utils.logger import setup_logger
    setup_logger()
    from loguru import logger
    logger.info("Graph execution started")
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_file: str | Path = "data/competitive-analysis.log") -> None:
    """Configure Loguru with console and rotating file sinks.

    Removes any default Loguru handler first, then adds:
      1. A colorized stdout sink at INFO level.
      2. A file sink at DEBUG level that rotates at 10 MB and retains logs
         for 1 month.

    Args:
        log_file: Path to the log file. Defaults to "data/competitive-analysis.log".
                  The parent directory is created automatically by Loguru if missing.
    """
    # Remove the default Loguru handler (stderr with simple format).
    logger.remove()

    # Console sink — colorized output for interactive debugging.
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        level="INFO",
    )

    # File sink — structured logs for post-mortem analysis.
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="1 month",
    )