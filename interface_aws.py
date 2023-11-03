import boto3

class InterfaceAWS:
    def __init__(self) -> None:
        self.s3_client = boto3.client('s3')
    
    def get_object(self, s3_key: str, bucket_name: str):
        return self.s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    
    def delete_s3_object(self, s3_key: str, bucket_name: str):
        return self.s3_client.delete_object(Bucket=bucket_name, Key=s3_key)