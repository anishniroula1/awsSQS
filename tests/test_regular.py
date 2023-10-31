import pytest
from unittest.mock import MagicMock, patch
import regular  # Replace with the name of your script file

def test_create_queue():
    mock_sqs = MagicMock()
    mock_sqs.create_queue.return_value = {'QueueUrl': 'http://example.com/queue'}
    with patch.object(regular, 'sqs', mock_sqs):
        queue_url = regular.create_queue('TestQueue')
        assert queue_url == 'http://example.com/queue'

def test_send_message():
    mock_sqs = MagicMock()
    with patch.object(regular, 'sqs', mock_sqs):
        regular.send_message('http://example.com/queue', 'Hello, World!')

def test_receive_messages():
    mock_sqs = MagicMock()
    mock_sqs.receive_message.return_value = {'Messages': [{'MessageId': '1', 'Body': 'Hello, World!'}]}
    with patch.object(regular, 'sqs', mock_sqs):
        messages = regular.receive_messages('http://example.com/queue')
        assert len(messages) == 1
        assert messages[0]['Body'] == 'Hello, World!'

def test_delete_messages():
    mock_sqs = MagicMock()
    with patch.object(regular, 'sqs', mock_sqs):
        regular.delete_messages('http://example.com/queue', [{'MessageId': '1', 'ReceiptHandle': 'r-handle'}])

def test_process_message(capfd):
    message = {'Body': 'Hello, World!', 'MessageAttributes': {'Attribute1': {'StringValue': 'Value1'}}}
    regular.process_message(message)
    out, err = capfd.readouterr()
    assert 'Processing message: Hello, World!' in out
    assert ' - Attribute1: Value1' in out
