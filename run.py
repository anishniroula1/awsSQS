import logging

from CutomLogger import CustomFormatter, CustomLogger
from loggin_handler import MyHandler
from objectTest import get_logs


logging.setLoggerClass(CustomLogger)

# Usage
logger = logging.getLogger("myLogger")
logger.setLevel(logging.INFO)

# Custom handler setup
logger.addHandler(MyHandler())

# Log messages
logger.info("This log shows the default message", show_default=True)
logger.info("This log does not show the default message")
get_logs()