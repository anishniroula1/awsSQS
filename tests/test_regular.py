import pytest
from unittest.mock import MagicMock, patch

from regular import create_queue, send_message

@patch('regular.boto3.client')
def test_create_queue(mock_client):
    mock_client.return_value.create_queue.return_value = {'QueueUrl': 'http://example.com/queue'}
    result = create_queue('test_queue')
    print(result)
    assert result == 'http://example.com/queue'

@patch('regular.boto3.client')
def test_send_message(mock_client):
    mock_client.return_value.send_message.return_value = {'MessageId': '123456'}
    result = send_message('http://example.com/queue', 'Hello, World!')
    assert result is None  # Since send_message doesn't return anything

# ... similarly for other functions
