import logging


def get_logs():
    logger = logging.getLogger("myLogger")
    logger.info("Hi there , from another file")
