import logging
import inspect
import os

class CustomLogger:
    DEFAULT_MESSAGE = os.getenv("LOGGER_VARIABLE", "")

    def __init__(self, name="customLogger", level=logging.INFO):
        # Setup the internal logger
        self.internal_logger = logging.getLogger(name)
        self.internal_logger.setLevel(level)
        if not self.internal_logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.internal_logger.addHandler(ch)

    @classmethod
    def set_generic_message(cls, message: str):
        cls.DEFAULT_MESSAGE = message

    def _find_caller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        frame = inspect.currentframe()
        if frame is not None:
            frame = frame.f_back
        while frame:
            frame_info = inspect.getframeinfo(frame)
            filename = frame_info.filename
            if "logging" not in filename and filename != __file__:
                # Return caller's information
                return filename, frame_info.lineno
            frame = frame.f_back
        return None, None  # Default if no caller was found

    def _log(self, level, message, *args, **kwargs):
        # Include the default message if set
        if CustomLogger.DEFAULT_MESSAGE:
            message = f"{CustomLogger.DEFAULT_MESSAGE} {message}"
        
        # Find the caller's information
        filename, lineno = self._find_caller()
        if filename and lineno:
            message = f"{filename}:{lineno} - {message}"

        # Log the message with the internal logger
        self.internal_logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

# # Example usage
# if __name__ == "__main__":
#     CustomLogger.set_generic_message("Global Message:")
#     logger = CustomLogger()
#     logger.info("This is an informational message.")
