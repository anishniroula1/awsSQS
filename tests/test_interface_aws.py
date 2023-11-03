import boto3
from interface_aws import InterfaceAWS
from moto import mock_s3

@mock_s3
def test_get_object():
    # Set up the mocked S3 environment
    conn = boto3.resource('s3', region_name='us-east-1')
    bucket_name = 'test-bucket'
    s3_key = 'test-key'
    conn.create_bucket(Bucket=bucket_name)
    conn.Object(bucket_name, s3_key).put(Body='Testing')

    # Create an instance of InterfaceAWS and call get_object
    interface_aws = InterfaceAWS()
    result = interface_aws.get_object(s3_key, bucket_name)
    body = result['Body'].read().decode('utf-8')

    assert body == 'Testing', f'Expected "Testing" but got "{body}"'
