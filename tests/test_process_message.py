import pytest
from unittest.mock import patch, MagicMock

from test_sub_flow import process_message


# Mock the S3 client to prevent actual AWS calls
@pytest.fixture
def mock_s3_client():
    with patch("boto3.client") as mock:
        yield mock


@pytest.fixture
def mock_prefect_task():
    with patch("prefect.task", side_effect=lambda f: f) as mock:
        yield mock


# Test when message is None
def test_process_message_none(mock_prefect_task):
    result = process_message(None)
    assert result is None


# Test when message is valid but the S3 object does not exist
def test_process_message_valid_but_no_s3_object(mock_s3_client, mock_prefect_task):
    mock_s3_client.return_value.get_object.side_effect = Exception(
        "S3 Object not found"
    )

    message = {"id": "some-id", "bucket_name": "bucket", "s3_key": "key"}
    result = process_message(message)
    assert result is None


# Test when message is valid and S3 object is retrieved
def test_process_message_valid_with_s3_object(mock_s3_client, mock_prefect_task):
    mock_response = {
        "Body": MagicMock(read=MagicMock(return_value=b"some data")),
        "ContentLength": 9,
    }
    mock_s3_client.return_value.get_object.return_value = mock_response

    message = {"id": "some-id", "bucket_name": "bucket", "s3_key": "key"}
    result = process_message(message)
    assert result == {"document_bytestream": b"some data", "file_size": 9}


# Test when message is valid and S3 object retrieval fails
def test_process_message_valid_with_s3_failure(mock_s3_client, mock_prefect_task):
    mock_s3_client.return_value.get_object.side_effect = Exception(
        "Failed to retrieve S3 Object"
    )

    message = {"id": "some-id", "bucket_name": "bucket", "s3_key": "key"}
    result = process_message(message)
    assert result is None
