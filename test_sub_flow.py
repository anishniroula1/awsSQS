import prefect
import boto3

class InterfaceAWS:
    def __init__(self) -> None:
        self.s3_client = boto3.client('s3')
    
    def get_object(self, s3_key: str, bucket_name: str):
        return self.s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    
    def delete_s3_object(self, s3_key: str, bucket_name: str):
        return self.s3_client.delete_object(Bucket=bucket_name, Key=s3_key)

@prefect.task
def retrieve_document_from_s3(document):
    if document.get('id') is None or document.get('bucket_name') is None or document.get('s3_key') is None:
        return None
    file_detail = {}
    try: 
        aws = InterfaceAWS()
        s3_document = aws.get_object(document.get('bucket_name'), document.get('s3_key'))
        file_detail['document_bytestream'] = s3_document.get("Body").read()
        file_detail["file_size"] = s3_document.get("ContentLength", -1)
        return file_detail
    except Exception as e:
        print("Failed")
        return None

@prefect.task
def print_result(message):
    return message

@prefect.flow
def process_message(message):
    if message is None:
        return None

    get_doc = retrieve_document_from_s3(message)
    get_msz = print_result(message=get_doc, wait_for=[get_doc])
    return get_msz