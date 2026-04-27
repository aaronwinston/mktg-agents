from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from config import settings


_CONFIGURED = False


def configure_logging() -> None:
    """Configure application logging.

    - Console logging for local development
    - File logging with daily rotation + retention
    """

    global _CONFIGURED
    if _CONFIGURED:
        return

    log_level_name = getattr(settings, "LOG_LEVEL", "INFO")
    level = getattr(logging, str(log_level_name).upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if running under reload / tests
    if root.handlers:
        _CONFIGURED = True
        return

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    log_dir = Path(getattr(settings, "LOG_DIR", Path(__file__).parent / "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    retention_days = int(getattr(settings, "LOG_RETENTION_DAYS", 14))
    file_handler = TimedRotatingFileHandler(
        filename=str(log_dir / "api.log"),
        when="D",
        interval=1,
        backupCount=retention_days,
        encoding="utf-8",
        utc=True,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    _CONFIGURED = True
