"""
s3io.py

S3 utilities for Lambda:
- download to /tmp
- read JSON / JSONL
- upload JSON
"""

from __future__ import annotations

import json
import logging
from typing import Any, List

import boto3

s3 = boto3.client("s3")


def download_to_tmp(bucket: str, key: str, filename: str, logger: logging.Logger | None = None) -> str:
    log = logger or logging.getLogger(__name__)
    local_path = f"/tmp/{filename}"
    log.info("Downloading s3://%s/%s -> %s", bucket, key, local_path)
    s3.download_file(bucket, key, local_path)
    return local_path


def read_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl_file(path: str) -> List[Any]:
    out: List[Any] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def upload_json(bucket: str, key: str, data: Any, logger: logging.Logger | None = None) -> None:
    log = logger or logging.getLogger(__name__)
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    log.info("Uploading JSON to s3://%s/%s (%d bytes)", bucket, key, len(body))
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
