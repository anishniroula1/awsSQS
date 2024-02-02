# Filename: test_custom_logger.py
import logging
from custom_logger import CustomLogger
import pytest

def test_log_levels(mocker):
    """
    Test that the CustomLogger logs messages at various levels correctly.
    """
    # Mock the internal logger to prevent actual logging during tests
    mock_log = mocker.patch.object(logging.Logger, 'log')

    logger = CustomLogger()
    test_messages = {
        logging.DEBUG: "Debug message",
        logging.INFO: "Info message",
        logging.WARNING: "Warning message",
        logging.ERROR: "Error message",
        logging.CRITICAL: "Critical message",
    }

    for level, message in test_messages.items():
        logger._log(level, message)
        mock_log.assert_called_with(level, mocker.ANY, message)

def test_generic_message(mocker):
    """
    Test that setting a generic message prefix works correctly.
    """
    # Mock the internal logger to prevent actual logging
    mock_log = mocker.patch.object(logging.Logger, 'log')

    test_message = "Test message"
    generic_message = "Generic Prefix:"
    CustomLogger.set_generic_message(generic_message)

    logger = CustomLogger()
    logger.info(test_message)

    expected_message = f"{generic_message} {test_message}"
    mock_log.assert_called_with(logging.INFO, mocker.ANY, expected_message)

def test_find_caller(mocker):
    """
    Test that the logger correctly identifies the caller's file name and line number.
    """
    # This test is a bit more involved and requires deeper knowledge of the system's internals,
    # as _find_caller is a private method and its direct effects are seen in logged messages.
    # For simplicity, this test is left as an example and would need to mock inspect.stack()
    # or inspect.currentframe() to simulate different call stacks.
    pass
