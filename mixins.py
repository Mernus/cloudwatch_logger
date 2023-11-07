import logging
import sys

class ConsoleLoggingMixin:
    """Mixin for logging to console."""
    def __init__(self) -> None:
        self.logger = self._init_logger()

    def _init_logger(self) -> logging.Logger:
        """Initialize logger with output in stdout.

        Returns:
            logging.Logger: Logger.
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        log_format = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(log_format)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger
