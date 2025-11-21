import csv
import importlib
import io
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import boto3
import pytest
from moto import mock_aws

# Ensure the project root (containing src/) is importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import modules up front so reload can work after env is set.
from src.lambdas import common, data_preparation


def _put_text(s3_client, bucket: str, key: str, body: str) -> None:
    s3_client.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))


def _put_csv(s3_client, bucket: str, key: str, rows: List[Dict[str, str]]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["File", "Line", "Begin Offset", "End Offset", "Type"]
    )
    writer.writeheader()
    writer.writerows(rows)
    s3_client.put_object(Bucket=bucket, Key=key, Body=buf.getvalue().encode("utf-8"))


def _get_lines(s3_client, bucket: str, key: str) -> List[str]:
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8").splitlines()


def _s3_event(bucket: str, text_key: str, csv_key: str) -> Dict:
    return {
        "Records": [
            {"s3": {"bucket": {"name": bucket}, "object": {"key": text_key}}},
            {"s3": {"bucket": {"name": bucket}, "object": {"key": csv_key}}},
        ]
    }


@pytest.fixture
def prep_env(monkeypatch) -> Tuple[str, boto3.client, object]:
    """
    Spin up a moto-backed S3, set required env vars, reload modules so they bind to the mock.
    """
    with mock_aws():
        bucket = "test-bucket"
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket=bucket)

        # Use the defaults from the code (hardcoded prefixes/base name) and only set sample fraction/process flag.
        monkeypatch.delenv("PREPARED_PREFIX", raising=False)
        monkeypatch.delenv("RUN_ANALYSIS_PREFIX", raising=False)
        monkeypatch.delenv("READY_TO_TRAIN_PREFIX", raising=False)
        monkeypatch.delenv("TRAINING_DOCS_PREFIX", raising=False)
        monkeypatch.delenv("DATASET_BASE_NAME", raising=False)
        monkeypatch.setenv("SAMPLE_FRACTION", "0.1")
        monkeypatch.setenv("PROCESS_ANALYSIS", "true")

        # Reload modules after mock + env are set so clients pick up the mock.
        importlib.reload(common)
        importlib.reload(data_preparation)

        # Make sampling deterministic across runs.
        random.seed(1234)

        yield bucket, s3_client, data_preparation


def test_prepare_new_dataset_creates_version_and_splits(prep_env):
    bucket, s3_client, data_preparation = prep_env

    text_key = "training_docs/new.txt"
    annotations_key = "training_docs/new.csv"
    text_body = "\n".join([f"line {i}" for i in range(1, 11)])  # 10 lines
    _put_text(s3_client, bucket, text_key, text_body)
    _put_csv(
        s3_client,
        bucket,
        annotations_key,
        [
            {"File": "prepare_training_doc_v1.txt", "Line": "2", "Begin Offset": "0", "End Offset": "4", "Type": "FTO"},
            {"File": "prepare_training_doc_v1.txt", "Line": "5", "Begin Offset": "0", "End Offset": "4", "Type": "OFAC ORG"},
        ],
    )

    response = data_preparation.handler(_s3_event(bucket, text_key, annotations_key), {})

    # Versioning and counts.
    assert response["dataset_version"] == 1
    assert response["run_analysis"]["line_count"] + response["ready_to_train"]["line_count"] == 10

    # Prepared artifacts have new naming (_annotation for csv).
    assert response["prepared"]["text_key"].endswith("prepare_training_doc_v1.txt")
    assert response["prepared"]["annotations_key"].endswith("prepare_annotation_v1.csv")
    prepared_txt = _get_lines(s3_client, bucket, response["prepared"]["text_key"])
    assert prepared_txt == text_body.splitlines()

    # Splits land in the right prefixes with analysis/ready naming.
    assert response["run_analysis"]["text_key"].endswith("analysis_training_doc_v1.txt")
    assert response["run_analysis"]["annotations_key"].endswith("analysis_annotation_v1.csv")
    assert response["ready_to_train"]["text_key"].endswith("train_training_doc_v1.txt")
    assert response["ready_to_train"]["annotations_key"].endswith("train_annotation_v1.csv")

    analysis_lines = _get_lines(s3_client, bucket, response["run_analysis"]["text_key"])
    train_lines = _get_lines(s3_client, bucket, response["ready_to_train"]["text_key"])
    assert len(analysis_lines) == response["run_analysis"]["line_count"]
    assert len(train_lines) == response["ready_to_train"]["line_count"]
    assert len(analysis_lines) + len(train_lines) == len(prepared_txt)


def test_prepare_appends_to_existing_dataset(prep_env):
    bucket, s3_client, data_preparation = prep_env

    # Seed existing prepared v1.
    _put_text(s3_client, bucket, "prepared_data/prepare_training_doc_v1.txt", "old1\nold2")
    _put_csv(
        s3_client,
        bucket,
        "prepared_data/annotation_v1.csv",
        [
            {"File": "prepare_training_doc_v1.txt", "Line": "1", "Begin Offset": "0", "End Offset": "4", "Type": "FTO"},
            {"File": "prepare_training_doc_v1.txt", "Line": "2", "Begin Offset": "0", "End Offset": "4", "Type": "OFAC POI"},
        ],
    )

    # New upload to append.
    text_key = "training_docs/newer.txt"
    annotations_key = "training_docs/newer.csv"
    _put_text(s3_client, bucket, text_key, "new1\nnew2")
    _put_csv(
        s3_client,
        bucket,
        annotations_key,
        [{"File": "training_doc_v2.txt", "Line": "1", "Begin Offset": "0", "End Offset": "4", "Type": "OFAC ORG"}],
    )

    response = data_preparation.handler(_s3_event(bucket, text_key, annotations_key), {})

    assert response["dataset_version"] == 2
    assert response["prepared"]["annotations_key"].endswith("prepare_annotation_v2.csv")

    prepared_txt = _get_lines(s3_client, bucket, response["prepared"]["text_key"])
    # Expect old lines then new lines.
    assert prepared_txt == ["old1", "old2", "new1", "new2"]

    # Ensure split sizes add up and at least one line was held out.
    assert response["run_analysis"]["line_count"] >= 1
    assert response["ready_to_train"]["line_count"] >= 1
    assert response["run_analysis"]["line_count"] + response["ready_to_train"]["line_count"] == 4

    # Annotations were rewritten to the new combined name and new file names.
    analysis_csv = _get_lines(s3_client, bucket, response["run_analysis"]["annotations_key"])
    assert analysis_csv[0] == "File,Line,Begin Offset,End Offset,Type"
    assert all("analysis_training_doc_v2.txt" in row for row in analysis_csv[1:])


def test_s3_event_missing_csv_raises(prep_env):
    bucket, s3_client, data_preparation = prep_env
    bad_event = {
        "Records": [
            {"s3": {"bucket": {"name": bucket}, "object": {"key": "training_docs/only.txt"}}},
        ]
    }
    with pytest.raises(data_preparation.DataPreparationError):
        data_preparation.handler(bad_event, {})


def test_process_analysis_false_routes_all_to_training(prep_env, monkeypatch):
    bucket, s3_client, data_preparation = prep_env
    # Turn off analysis split.
    monkeypatch.setenv("PROCESS_ANALYSIS", "false")
    importlib.reload(data_preparation)

    text_key = "training_docs/one.txt"
    annotations_key = "training_docs/one.csv"
    _put_text(s3_client, bucket, text_key, "only line")
    _put_csv(
        s3_client,
        bucket,
        annotations_key,
        [{"File": "prepare_training_doc_v1.txt", "Line": "0", "Begin Offset": "0", "End Offset": "4", "Type": "FTO"}],
    )

    response = data_preparation.handler(_s3_event(bucket, text_key, annotations_key), {})

    assert response["process_analysis"] is False
    assert response["run_analysis"]["line_count"] == 0
    assert response["ready_to_train"]["line_count"] == 1
