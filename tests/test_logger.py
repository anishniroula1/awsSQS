# Filename: test_custom_logger.py
import logging
import sys
from io import StringIO
import pytest

from CutomLogger import CustomLogger

@pytest.fixture
def logger():
    """Fixture to provide a CustomLogger instance."""
    CustomLogger.set_generic_message("")  # Reset generic message to default for each test
    return CustomLogger()

@pytest.fixture
def capture_log_output():
    """Fixture to capture log output."""
    original_stdout = sys.stdout  # Save a reference to the original standard output
    sys.stdout = StringIO()  # Redirect standard output to a StringIO object.
    yield sys.stdout
    sys.stdout = original_stdout  # Reset the standard output to its original value

def test_log_info_level(logger, capture_log_output):
    logger.info("This is an informational message.")
    assert "INFO" in capture_log_output.getvalue()
    assert "This is an informational message." in capture_log_output.getvalue()

def test_generic_message_effect(logger, capture_log_output):
    CustomLogger.set_generic_message("Generic Prefix:")
    logger.info("Test message with prefix.")
    output = capture_log_output.getvalue()
    assert "Generic Prefix:" in output
    assert "Test message with prefix." in output

def test_different_log_levels(logger, capture_log_output):
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    output = capture_log_output.getvalue()
    assert "DEBUG" in output
    assert "WARNING" in output
    assert "ERROR" in output
    assert "CRITICAL" in output

# Since testing private methods like _find_caller directly is not a best practice in unit testing,
# and because its functionality is inherently covered by testing the output of the public logging methods,
# it's not included as a separate test case here.

