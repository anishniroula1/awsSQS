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

# Set the custom logger class as the default for new loggers
