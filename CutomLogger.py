import logging

class CustomLogger(logging.Logger):
    DEFAULT_MESSAGE = "Default Message: "

    def _log(self, level, msg, args, kwargs):
        super()._log(level, msg, args, **kwargs)

    def debug(self, msg, show_default=False, *args, **kwargs):
        self._log(logging.DEBUG, msg, args, kwargs)

    def info(self, msg, show_default=False, *args, **kwargs):
        self._log(logging.INFO, msg, args, kwargs)

    def warning(self, msg, show_default=False, *args, **kwargs):
        self._log(logging.WARNING, msg, args, kwargs)

    def error(self, msg, show_default=False, *args, **kwargs):
        self._log(logging.ERROR, msg, args, kwargs)

    def critical(self, msg, show_default=False, *args, **kwargs):
        self._log(logging.CRITICAL, msg, args, kwargs)

# Set the custom logger class as the default for new loggers
logging.setLoggerClass(CustomLogger)

# Usage
logger = logging.getLogger("myCustomLogger")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Log with default message
logger.info("This log shows the default message", False)

# Log without default message
logger.info("This log does not show the default message")
