import pytest
import boto3
from moto import mock_s3

from retrive_document_from_s3 import Document, retrieve_document_from_s3

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture
def s3(aws_credentials):
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')


def test_retrieve_document_from_s3(s3):
    # Create a mock S3 bucket and object
    bucket_name = 'my-bucket'
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key='test.txt', Body=b'Hello, world')

    # Create a Document object
    document = Document(id='1', bucket_name=bucket_name, s3_key='test.txt')

    # Test the function
    file_detail = retrieve_document_from_s3(document)
    breakpoint()
    assert file_detail['document_bytestream'] == b'Hello, world'
    assert file_detail['file_size'] == 12

    # Test with missing values
    invalid_document = Document(id=None, bucket_name=bucket_name, s3_key='test.txt')
    assert retrieve_document_from_s3(invalid_document) is None

    # Test with non-existent s3 key
    non_existent_document = Document(id='1', bucket_name=bucket_name, s3_key='non-existent.txt')
    assert retrieve_document_from_s3(non_existent_document) is None
