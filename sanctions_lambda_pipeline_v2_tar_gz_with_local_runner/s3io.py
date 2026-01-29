"""
s3io.py

S3 I/O + Comprehend tar.gz extraction helpers.

This module can be imported even if boto3 is not installed.
- Local runs do not require S3.
- Lambda runs always have boto3.

If boto3 is missing:
- download_to_tmp / upload_json raise a clear error.
- tar extraction + local JSON/JSONL reading still works.
"""

from __future__ import annotations

import json
import logging
import tarfile
from pathlib import Path
from typing import Any, List, Optional

try:
    import boto3  # type: ignore
    _s3 = boto3.client("s3")
except Exception:
    _s3 = None


def download_to_tmp(bucket: str, key: str, filename: str, logger: Optional[logging.Logger] = None) -> str:
    """Download an S3 object to `/tmp/<filename>` and return the local path."""
    if _s3 is None:
        raise RuntimeError("boto3 is not available. download_to_tmp requires boto3 for S3 access.")
    log = logger or logging.getLogger(__name__)
    local_path = f"/tmp/{filename}"
    log.info("Downloading s3://%s/%s -> %s", bucket, key, local_path)
    _s3.download_file(bucket, key, local_path)
    return local_path


def upload_json(bucket: str, key: str, data: Any, logger: Optional[logging.Logger] = None) -> None:
    """Upload a Python object as JSON to S3."""
    if _s3 is None:
        raise RuntimeError("boto3 is not available. upload_json requires boto3 for S3 access.")
    log = logger or logging.getLogger(__name__)
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    log.info("Uploading JSON to s3://%s/%s (%d bytes)", bucket, key, len(body))
    _s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")


def extract_comprehend_tar_gz(
    tar_gz_path: str,
    extract_dir: str = "/tmp/comprehend_extract",
    preferred_member: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> str:
    """
    Extract a Comprehend `output.tar.gz` and return the path to the JSONL file inside.

    Comprehend batch/async jobs commonly output a tarball, and the JSONL member
    inside may have **no extension**.

    Auto-detection:
    - extract everything
    - pick the largest non-empty extracted file
    - prefer a JSON-looking header ({ or [) if possible
    """
    log = logger or logging.getLogger(__name__)
    extract_path = Path(extract_dir)

    # Clean extract dir (warm-start safety)
    if extract_path.exists():
        for p in sorted(extract_path.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                try:
                    p.rmdir()
                except Exception:
                    pass
    extract_path.mkdir(parents=True, exist_ok=True)

    log.info("Extracting tar.gz %s -> %s", tar_gz_path, extract_dir)

    with tarfile.open(tar_gz_path, "r:gz") as tf:
        members = tf.getmembers()

        if preferred_member:
            m = next((x for x in members if x.name == preferred_member), None)
            if not m:
                raise ValueError(f"preferred_member '{preferred_member}' not found in tar.gz")
            tf.extract(m, path=extract_dir)
            candidate = extract_path / m.name
            if candidate.is_file() and candidate.stat().st_size > 0:
                return str(candidate)
            raise ValueError(f"preferred_member '{preferred_member}' extracted but file is empty/missing")

        tf.extractall(path=extract_dir)

    files = [p for p in extract_path.rglob("*") if p.is_file()]
    if not files:
        raise ValueError("No files found inside Comprehend tar.gz after extraction.")

    files.sort(key=lambda p: p.stat().st_size, reverse=True)

    def is_jsonish(p: Path) -> bool:
        try:
            with open(p, "rb") as f:
                head = f.read(256).lstrip()
            return head.startswith(b"{") or head.startswith(b"[")
        except Exception:
            return False

    for p in files:
        if p.stat().st_size <= 0:
            continue
        if is_jsonish(p):
            return str(p)

    for p in files:
        if p.stat().st_size > 0:
            return str(p)

    raise ValueError("All extracted files were empty; cannot locate JSONL output.")


def read_json_file(path: str) -> Any:
    """Read JSON from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl_file(path: str) -> List[Any]:
    """Read JSONL from disk (one JSON object per line)."""
    out: List[Any] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out
