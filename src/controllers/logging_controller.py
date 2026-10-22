"""Asynchronous file logging without changing the application's root logger."""

import asyncio
import logging
from pathlib import Path


class LoggingController:
    """Own one file handler, which callers can explicitly close."""

    def __init__(self, log_file="logs/error_log.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.Logger(f"robot_companion.{id(self)}", logging.DEBUG)
        self._logger.propagate = False
        self._handler = logging.FileHandler(self.log_file, encoding="utf-8")
        self._handler.setFormatter(logging.Formatter(
            "%(levelname)s | %(asctime)s | %(message)s"
        ))
        self._logger.addHandler(self._handler)

    async def log(self, message, error_level):
        """Write a supported level through a worker thread."""
        await asyncio.to_thread(self._log, message, error_level)

    def _log(self, message, error_level):
        supported = {
            logging.DEBUG, logging.INFO, logging.WARNING,
            logging.ERROR, logging.CRITICAL,
        }
        if error_level in supported:
            self._logger.log(error_level, message)
        else:
            self._logger.warning(
                "Unsupported logging level %r: %s", error_level, message
            )

    def close(self):
        """Release this controller's handler without touching other loggers."""
        self._logger.removeHandler(self._handler)
        self._handler.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


async def main():
    """Run a logging-only example when explicitly requested."""
    with LoggingController() as logger:
        await logger.log("Logging example", logging.INFO)


if __name__ == "__main__":
    asyncio.run(main())
