# tests/test_lambda_handler_end_to_end.py
"""
End-to-end (component) test for `handler.lambda_handler`.

What it tests:
- Uploads 3 inputs to mocked S3:
  1) Sanctions CSV (with your real headers)
  2) Mapping JSON list [{globalId, line, content}, ...]
  3) Comprehend output.tar.gz containing a JSONL member (no extension needed)
- Sets Lambda env vars
- Calls handler.lambda_handler(...)
- Verifies output was written to S3 and contains:
  - sanctionFlag = True
  - sanctionId (from "Full ID")
  - sanctionEntityType (from "ns1_entityType")

Requirements:
- pytest
- moto
- boto3
"""

import io
import json
import csv
import tarfile
from pathlib import Path

import pytest

moto = pytest.importorskip("moto")
from moto import mock_aws  # moto v5+
import boto3

import handler


def _make_comprehend_tar_gz_bytes(jsonl_text: str, member_name: str = "part-00000") -> bytes:
    """
    Build a tar.gz in-memory that looks like Comprehend output:
    - manifest.json
    - one JSONL member (often named part-00000 / part-00001 etc.)
    """
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        # manifest
        manifest_bytes = json.dumps({"job": "comprehend"}).encode("utf-8")
        manifest_info = tarfile.TarInfo(name="manifest.json")
        manifest_info.size = len(manifest_bytes)
        tf.addfile(manifest_info, io.BytesIO(manifest_bytes))

        # jsonl member (no extension needed)
        member_bytes = jsonl_text.encode("utf-8")
        member_info = tarfile.TarInfo(name=member_name)
        member_info.size = len(member_bytes)
        tf.addfile(member_info, io.BytesIO(member_bytes))

    buf.seek(0)
    return buf.read()


@mock_aws
def test_lambda_handler_end_to_end_s3(tmp_path: Path, monkeypatch):
    # -----------------------------
    # 1) Setup mocked S3 buckets
    # -----------------------------
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="in-bucket")
    s3.create_bucket(Bucket="out-bucket")

    # -----------------------------
    # 2) Upload sanctions CSV
    #    (REAL headers)
    # -----------------------------
    sanctions_csv_path = tmp_path / "sanctions.csv"
    with sanctions_csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["Full ID", "ns1_entityType", "ns1_formattedFullName"],
        )
        w.writeheader()
        # Individual row uses "Last, First" -> should become "Jon Julu"
        w.writerow(
            {
                "Full ID": "A1",
                "ns1_entityType": "Individual",
                "ns1_formattedFullName": "Julu, Jon;IS",
            }
        )
        # Entity row
        w.writerow(
            {
                "Full ID": "B2",
                "ns1_entityType": "Entity",
                "ns1_formattedFullName": "Exxon, Inc",
            }
        )

    s3.put_object(Bucket="in-bucket", Key="sanctions.csv", Body=sanctions_csv_path.read_bytes())

    # -----------------------------
    # 3) Upload mapping JSON list
    # -----------------------------
    mapping = [
        {"globalId": "g1", "line": 1, "content": "I met Jon Julu yesterday."},
        {"globalId": "g2", "line": 2, "content": "Payment sent to Exxon, Inc."},
        {"globalId": "g3", "line": 3, "content": "this is yellow"},  # should NOT be sanctioned by IS
    ]
    s3.put_object(Bucket="in-bucket", Key="mapping.json", Body=json.dumps(mapping).encode("utf-8"))

    # -----------------------------
    # 4) Upload Comprehend tar.gz
    #    (Title Case keys inside Entities)
    # -----------------------------
    jsonl_text = "\n".join(
        [
            json.dumps(
                {
                    "Line": 1,
                    "Entities": [
                        {
                            "Text": "Jon Julu",
                            "BeginOffset": 6,
                            "EndOffset": 13,
                            "Type": "PERSON",
                            "Score": 0.95,
                        }
                    ],
                }
            ),
            json.dumps(
                {
                    "Line": 2,
                    "Entities": [
                        {
                            "Text": "Exxon, Inc",
                            "BeginOffset": 16,
                            "EndOffset": 25,
                            "Type": "ORGANIZATION",
                            "Score": 0.99,
                        }
                    ],
                }
            ),
            json.dumps(
                {
                    "Line": 3,
                    "Entities": [
                        # even if Comprehend says ORG, ignore_words should prevent IS being treated as sanctioned
                        {
                            "Text": "is",
                            "BeginOffset": 5,
                            "EndOffset": 7,
                            "Type": "ORGANIZATION",
                            "Score": 0.80,
                        }
                    ],
                }
            ),
        ]
    ) + "\n"

    tar_bytes = _make_comprehend_tar_gz_bytes(jsonl_text, member_name="part-00000")
    s3.put_object(Bucket="in-bucket", Key="output.tar.gz", Body=tar_bytes)

    # -----------------------------
    # 5) Set Lambda env vars
    # -----------------------------
    monkeypatch.setenv("SANCTIONS_BUCKET", "in-bucket")
    monkeypatch.setenv("SANCTIONS_KEY", "sanctions.csv")
    monkeypatch.setenv("MAPPING_BUCKET", "in-bucket")
    monkeypatch.setenv("MAPPING_KEY", "mapping.json")
    monkeypatch.setenv("COMPREHEND_BUCKET", "in-bucket")
    monkeypatch.setenv("COMPREHEND_KEY", "output.tar.gz")

    # Write output back to S3 (optional behavior)
    monkeypatch.setenv("OUTPUT_BUCKET", "out-bucket")
    monkeypatch.setenv("OUTPUT_KEY", "final.json")

    # Prevent false positives for IS/AS, etc.
    monkeypatch.setenv("IGNORE_WORDS", "is,as,the")

    # -----------------------------
    # 6) Invoke lambda handler
    # -----------------------------
    resp = handler.lambda_handler({}, None)
    assert resp["outputWritten"] is True

    # -----------------------------
    # 7) Validate output JSON in S3
    # -----------------------------
    obj = s3.get_object(Bucket="out-bucket", Key="final.json")
    payload = json.loads(obj["Body"].read().decode("utf-8"))

    # g1 should be sanctioned from Individual row A1
    g1 = next(r for r in payload["results"] if r["globalId"] == "g1")
    assert any(e.get("sanctionFlag") for e in g1["entities"])
    ent1 = next(e for e in g1["entities"] if e.get("sanctionFlag"))
    assert ent1["sanctionId"] == "A1"
    assert ent1["sanctionEntityType"] == "Individual"

    # g2 should be sanctioned from Entity row B2
    g2 = next(r for r in payload["results"] if r["globalId"] == "g2")
    ent2 = next(e for e in g2["entities"] if e.get("sanctionFlag"))
    assert ent2["sanctionId"] == "B2"
    assert ent2["sanctionEntityType"] == "Entity"

    # g3 should NOT be sanctioned (because "is" is ignored)
    g3 = next(r for r in payload["results"] if r["globalId"] == "g3")
    assert all(not e.get("sanctionFlag") for e in g3["entities"])
