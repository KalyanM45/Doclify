# logger.py
import logging
from datetime import datetime
from pathlib import Path

# Create log file ONCE
_current_date = datetime.now().strftime("%Y-%m-%d")
_current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

LOG_DIR = Path(".doclify") / "logs" / _current_date
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"{_current_timestamp}.log"

_LOGGING_CONFIGURED = False


def get_logger(name: str = __name__) -> logging.Logger:
    global _LOGGING_CONFIGURED

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not _LOGGING_CONFIGURED:
        formatter = logging.Formatter(
            "[%(asctime)s]: %(name)s: %(levelname)s: %(lineno)d: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)

        # Instead of root_logger, we use 'doclify' to capture our project's logs only
        project_logger = logging.getLogger("doclify")
        project_logger.setLevel(logging.DEBUG)
        project_logger.addHandler(file_handler)
        project_logger.addHandler(console_handler)
        project_logger.propagate = False  # Prevent logs from bubbling up to root

        # Silence common noisy libraries globally
        external_loggers = ["urllib3", "httpx", "httpcore", "aiohttp"]
        for logger_name in external_loggers:
            ext_logger = logging.getLogger(logger_name)
            ext_logger.setLevel(logging.WARNING)
            ext_logger.propagate = False  # Stop propagation for external loggers

        _LOGGING_CONFIGURED = True

    return logger