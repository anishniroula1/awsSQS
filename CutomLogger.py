import logging
import os

class CustomLogger:
    DEFAULT_MESSAGE = os.getenv("LOGGER_VARIABLE", "")

    def __init__(self, name="customLogger", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.hasHandlers():
            # Add a stream handler to the logger if it doesn't already have one
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def _log(self, level, message, args, **kwargs):
        # Prepend the default message if it's set
        if CustomLogger.DEFAULT_MESSAGE:
            message = f"{CustomLogger.DEFAULT_MESSAGE} {message}"
        self.logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, args, **kwargs)

    @classmethod
    def set_generic_message(cls, message: str):
        os.environ["LOGGER_VARIABLE"] = message
        cls.DEFAULT_MESSAGE = message

# Usage example
if __name__ == "__main__":
    CustomLogger.set_generic_message("SessionID:XYZ")
    log = CustomLogger()
    log.info("This is an informational message.")
