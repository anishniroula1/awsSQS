import inspect
import logging
import os

class CustomLogger(logging.Logger):
    
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def find_caller(self, stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        frame = inspect.currentframe()
        while frame:
            frame_info = inspect.getframeinfo(frame)
            filename = frame_info.filename
            # Check if the frame is outside of the logging module
            if "logging" not in filename and filename != __file__:
                return (filename, frame_info.lineno, frame_info.function, None)
            frame = frame.f_back
        return "(unknown file)", 0, "(unknown function)", None

    def _log_with_default_message(self, level, msg, args, kwargs, show_default):
        fn, lno, func, sinfo = self.find_caller()
        record = self.makeRecord(self.name, level, fn, lno, msg, args, kwargs, func)
        self.handle(record)

    def debug(self, msg, *args, show_default=False, **kwargs):
        self._log_with_default_message(logging.DEBUG, msg, args, kwargs, show_default)

    def info(self, msg, *args, show_default=False, **kwargs):
        self._log_with_default_message(logging.INFO, msg, args, kwargs, show_default)

    def warning(self, msg, *args, show_default=False, **kwargs):
        self._log_with_default_message(logging.WARNING, msg, args, kwargs, show_default)

    def error(self, msg, *args, show_default=False, **kwargs):
        self._log_with_default_message(logging.ERROR, msg, args, kwargs, show_default)

    def critical(self, msg, *args, show_default=False, **kwargs):
        self._log_with_default_message(logging.CRITICAL, msg, args, kwargs, show_default)


    @classmethod
    def set_generic_message(cls, message: str):
        """
        Sets a default message in an environment variable 'LOGGER_VARIABLE' 
        to be included in all log entries for the current session.

        This method is useful for appending a consistent context (like a session ID) 
        to logs across different parts of the application. It enhances log traceability 
        and correlation during a specific operation or session.

        Parameters:
        message (str): The message to be appended to log entries.

        Usage:
        - Invoke at the start of a session to set the message.
        - Unset (set to an empty string or None) at the session's end to avoid message persistence 
          in subsequent logs, which might cause misinterpretation.

        Example:
        CustomLogger.set_generic_message("SessionID:12345")
        # ... your code ...
        CustomLogger.set_generic_message("")  # Unsetting after use
        """
        os.environ["LOGGER_VARIABLE"] = message

    # ... rest of the CustomLogger methods ...


# Set the custom logger class as the default for new loggers
