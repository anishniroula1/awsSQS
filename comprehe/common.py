import json
import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def get_env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Fetch environment variables with optional default and required enforcement.
    """
    # Pull env var or fallback to default.
    val = os.environ.get(name, default)
    if required and val is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return val


def load_s3_text(bucket: str, key: str) -> str:
    """
    Get an object from S3 and decode as UTF-8 text.
    """
    # Fetch object then decode response bytes.
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")


def put_s3_text(bucket: str, key: str, body: str, content_type: str = "text/plain") -> None:
    """
    Persist a text payload to S3.
    """
    # Encode text as UTF-8 before upload; set content type for easier inspection.
    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType=content_type)
    logger.info("Uploaded %s/%s (%s bytes)", bucket, key, len(body))


def list_keys(bucket: str, prefix: str) -> List[str]:
    """
    List S3 object keys under a prefix.
    """
    keys: List[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    # Paginate to handle large listings.
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            keys.append(item["Key"])
    return keys


def json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to return JSON-serializable response.
    """
    return data
