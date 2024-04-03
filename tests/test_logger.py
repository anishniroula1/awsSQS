import logging
import pytest
from custom_logger import CustomLogger


class MemoryHandler(logging.Handler):
    """A logging handler that stores logs in a list."""

    def __init__(self):
        super().__init__()
        self.log_records = []

    def emit(self, record):
        self.log_records.append(record)


@pytest.fixture
def logger_with_memory_handler():
    """Fixture to provide a CustomLogger instance with a memory handler."""
    logger = CustomLogger(name="testLoggerWithMemoryHandler", level=logging.DEBUG)
    memory_handler = MemoryHandler()
    # Clear existing handlers and add our custom memory handler
    logger.internal_logger.handlers = []
    logger.internal_logger.addHandler(memory_handler)
    return logger, memory_handler


def test_log_info_level(logger_with_memory_handler):
    logger, memory_handler = logger_with_memory_handler
    logger.info("This is an informational message.")

    assert any(
        "This is an informational message." in record.msg
        for record in memory_handler.log_records
    )
    assert any(record.levelname == "INFO" for record in memory_handler.log_records)


def test_generic_message_effect(logger_with_memory_handler):
    logger, memory_handler = logger_with_memory_handler
    CustomLogger.set_generic_message("Generic Prefix:")
    logger.info("Test message with prefix.")

    assert any(
        "Generic Prefix: Test message with prefix." in record.msg
        for record in memory_handler.log_records
    )


def test_different_log_levels(logger_with_memory_handler):
    logger, memory_handler = logger_with_memory_handler
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    assert any(record.levelname == "DEBUG" for record in memory_handler.log_records)
    assert any(record.levelname == "WARNING" for record in memory_handler.log_records)
    assert any(record.levelname == "ERROR" for record in memory_handler.log_records)
    assert any(record.levelname == "CRITICAL" for record in memory_handler.log_records)
