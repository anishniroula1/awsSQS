import logging
from CutomLogger import CustomLogger

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("This is a debug message from test_logging.py")
