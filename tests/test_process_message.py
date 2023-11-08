import asyncio
import pytest
import boto3
from moto import mock_s3

from fifoSQS import process_message

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    boto3.setup_default_session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing",
    )

@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')

def test_process_message_none():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(process_message(None))
    assert result is None

def test_process_message_missing_keys(s3_client):
    loop = asyncio.get_event_loop()
    s3_client.create_bucket(Bucket='mybucket')
    message = {'id': '1234', 's3_key': 'file.txt'}  # Missing 'bucket_name'
    result = loop.run_until_complete(process_message(message))
    assert result is None

def test_process_message_s3_error(s3_client):
    loop = asyncio.get_event_loop()
    s3_client.create_bucket(Bucket='mybucket')
    message = {'id': '1234', 'bucket_name': 'mybucket', 's3_key': 'nonexistentfile.txt'}
    with pytest.raises(Exception):
        loop.run_until_complete(process_message(message))

def test_process_message_success(s3_client):
    loop = asyncio.get_event_loop()
    s3_client.create_bucket(Bucket='mybucket')
    s3_client.put_object(Bucket='mybucket', Key='file.txt', Body=b'file content')
    message = {'id': '1234', 'bucket_name': 'mybucket', 's3_key': 'file.txt'}
    result = loop.run_until_complete(process_message(message))
    assert result is not None
    assert result['file_size'] == len(b'file content')
