import logging
import os

class CustomFormatter(logging.Formatter):
    DEFAULT_MESSAGE = "Default Message: "

    def __init__(self, fmt, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record):
        if getattr(record, 'show_default', False):
            record.msg = f"{self.DEFAULT_MESSAGE}{record.msg}"
        return super().format(record)

class CustomLogger(logging.Logger):
    
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def find_caller(self, stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        orig_f = f
        while f and stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        if not f:
            f = orig_f
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == logging._srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name, None)
            break
        return rv

    def _log_with_default_message(self, level, msg, args, kwargs, show_default):
        fn, lno, func, sinfo = self.find_caller()
        # if show_default:
        #     msg = f"{self.DEFAULT_MESSAGE}{msg}"
        record = self.makeRecord(self.name, level, fn, lno, msg, args, kwargs, func)
        self.handle(record)

    def _log(self, level, msg, args, **kwargs):
        # extra = kwargs.pop('extra', {})
        # extra['show_default'] = kwargs.pop('show_default', False)
        super()._log(level, msg, args, kwargs)

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
