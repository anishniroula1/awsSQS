import logging
import inspect
import os
import threading

class CustomLogger:
    # Thread-local storage for unique message identifiers
    thread_context = threading.local()

    def __init__(self, name="customLogger", level=logging.INFO):
        self.internal_logger = logging.getLogger(name)
        self.internal_logger.setLevel(level)
        if not self.internal_logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)-10s %(message)s')
            ch.setFormatter(formatter)
            self.internal_logger.addHandler(ch)

    @classmethod
    def set_thread_message(cls, message: str):
        cls.thread_context.unique_message = message

    @classmethod
    def get_thread_message(cls):
        return getattr(cls.thread_context, 'unique_message', "")

    def _find_caller(self):
        frame = inspect.currentframe()
        if frame is not None:
            frame = frame.f_back.f_back  # Adjust this line to correctly skip the unnecessary frames
        while frame:
            frame_info = inspect.getframeinfo(frame)
            filename = os.path.basename(frame_info.filename)  # Use os.path.basename to get just the filename
            if "logging" not in filename and filename != os.path.basename(__file__):
                return filename, frame_info.lineno
            frame = frame.f_back
        return None, None

    def _log(self, level, message, *args, **kwargs):
        thread_message = CustomLogger.get_thread_message()
        if thread_message:
            message = f"{thread_message} {message}"
        filename, lineno = self._find_caller()
        if filename and lineno:
            level_name = logging.getLevelName(level)
            message = f"{filename}:{lineno} :{level_name}: {message}"
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
