import pytest
import logging
from io import StringIO
from custom_logger import CustomLogger  # Assuming your class is in custom_logger.py

# Fixture to set up the logger
@pytest.fixture
def setup_logger():
    logger = CustomLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger.addHandler(handler)

    return logger, log_stream

# Test for correct log message creation
def test_log_message(setup_logger):
    logger, log_stream = setup_logger
    test_message = "Test message"
    logger.info(test_message)
    log_stream.seek(0)
    assert test_message in log_stream.getvalue()

# Test for capturing caller information
def test_caller_info(setup_logger):
    logger, log_stream = setup_logger
    logger.info("Checking caller info")
    log_stream.seek(0)
    log_content = log_stream.getvalue()
    assert "test_custom_logger.py" in log_content  # Replace with the actual test file name
    assert "test_caller_info" in log_content  # Function name

# Test different logging levels
@pytest.mark.parametrize("level,method", [
    (logging.DEBUG, "debug"),
    (logging.INFO, "info"),
    (logging.WARNING, "warning"),
    (logging.ERROR, "error"),
    (logging.CRITICAL, "critical"),
])
def test_logging_levels(setup_logger, level, method):
    logger, log_stream = setup_logger
    getattr(logger, method)("Test message")
    log_stream.seek(0)
    assert log_stream.getvalue()  # Check if something was logged
