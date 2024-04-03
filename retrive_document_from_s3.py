from dataclasses import dataclass

import prefect

from interface_aws import InterfaceAWS


@dataclass
class Document:
    id: str
    bucket_name: str
    s3_key: str


@prefect.task
def retrieve_document_from_s3(document: Document):
    breakpoint()
    if document.id is None or document.bucket_name is None or document.s3_key is None:
        return None
    file_detail = {}
    try:
        aws = InterfaceAWS()
        s3_document = aws.get_object(document.bucket_name, document.s3_key)
        file_detail["document_bytestream"] = s3_document.get("Body").read()
        file_detail["file_size"] = s3_document.get("ContentLength", -1)
        return file_detail
    except Exception as e:
        print("Failed")
        return None
