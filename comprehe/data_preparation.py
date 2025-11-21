import csv
import io
import json
import logging
import random
import re
from typing import Dict, List, Tuple

from botocore.exceptions import BotoCoreError, ClientError

from .common import get_env, list_keys, load_s3_text, put_s3_text, s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REQUIRED_COLUMNS = ["file", "line", "BeginOffset", "EndOffset", "Type"]


class DataPreparationError(Exception):
    """Means data prep failed because something was wrong or S3 broke."""


def _extract_event_keys(event: Dict) -> Tuple[str, str, str]:
    """Get bucket and object keys out of the event."""
    # If the caller handed us the bucket and keys directly, use them.
    if "bucket" in event and "text_key" in event and "annotations_key" in event:
        return event["bucket"], event["text_key"], event["annotations_key"]

    # This path covers EventBridge style events.
    if event.get("detail"):
        detail = event["detail"]
        if "bucket" in detail and "object" in detail:
            bucket = detail["bucket"]["name"]
            text_key = detail["object"]["key"]
            raise ValueError(
                "Step input must include both text_key and annotations_key; "
                f"only saw {text_key}"
            )

    # This path covers S3 put events with both files.
    if "Records" in event:
        records = event["Records"]
        if len(records) < 2:
            raise ValueError(
                "S3 trigger must include both text and CSV objects; received fewer than 2 records"
            )
        bucket = records[0]["s3"]["bucket"]["name"]
        keys = [r["s3"]["object"]["key"] for r in records]
        text_key = next((k for k in keys if k.lower().endswith(".txt")), None)
        csv_key = next((k for k in keys if k.lower().endswith(".csv")), None)
        if not text_key or not csv_key:
            raise ValueError("S3 trigger missing txt or csv payload")
        return bucket, text_key, csv_key

    raise ValueError("Unsupported event shape; need bucket/text_key/annotations_key")


def _load_annotations(bucket: str, key: str) -> List[Dict]:
    # Grab the CSV file from S3.
    raw = load_s3_text(bucket, key)
    try:
        reader = csv.DictReader(io.StringIO(raw))
    except csv.Error as e:
        raise DataPreparationError(f"Failed to read annotations CSV {bucket}/{key}: {e}") from e

    # Make sure the header has all the columns we need.
    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise DataPreparationError(f"CSV missing required columns: {missing}")
    rows: List[Dict] = []
    for row in reader:
        # Turn strings into ints so math works later.
        rows.append(
            {
                "file": row["file"],
                "line": int(row["line"]),
                "BeginOffset": int(row["BeginOffset"]),
                "EndOffset": int(row["EndOffset"]),
                "Type": row["Type"],
            }
        )
    return rows


def _find_latest_version(bucket: str, prefix: str, base_name: str) -> Tuple[int, str, str]:
    """Find the newest prepared version already in S3."""
    # List every object under the prepared folder.
    try:
        keys = list_keys(bucket, prefix)
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"S3 error listing {bucket}/{prefix}: {e}") from e
    latest_version = 0
    latest_txt = ""
    latest_csv = ""
    # Match files like prepared_data/training_doc_v4.txt or .csv
    pattern = re.compile(rf"{re.escape(prefix)}{re.escape(base_name)}_v(\d+)\.(txt|csv)$")

    for key in keys:
        match = pattern.match(key)
        if not match:
            continue
        version = int(match.group(1))
        ext = match.group(2)
        if version >= latest_version:
            if ext == "txt":
                latest_txt = key
            elif ext == "csv":
                latest_csv = key
            latest_version = version
    return latest_version, latest_txt, latest_csv


def _write_csv(bucket: str, key: str, rows: List[Dict[str, str]]) -> None:
    # Turn rows into CSV text and upload.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    try:
        put_s3_text(bucket, key, output.getvalue(), content_type="text/csv")
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"Failed to write CSV to {bucket}/{key}: {e}") from e


def _safe_load_text(bucket: str, key: str, label: str) -> List[str]:
    """Load a text file from S3 and split by line, with nicer errors."""
    try:
        return load_s3_text(bucket, key).splitlines()
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"S3 error loading {label} at {bucket}/{key}: {e}") from e
    except Exception as e:
        raise DataPreparationError(f"Unable to load {label} at {bucket}/{key}: {e}") from e


def _merge_datasets(
    existing_lines: List[str],
    existing_annotations: List[Dict],
    new_lines: List[str],
    new_annotations: List[Dict],
    dataset_base_name: str,
    next_version: int,
) -> Tuple[List[str], List[Dict], str, str]:
    """Stick the new files on the end of the old ones and bump the version name."""
    combined_name = f"{dataset_base_name}_v{next_version}.txt"
    combined_annotation_name = f"{dataset_base_name}_v{next_version}.csv"

    # Merge the line buffers.
    combined_lines = [*existing_lines, *new_lines]
    line_offset = len(existing_lines)
    combined_annotations: List[Dict] = []

    # Copy forward existing annotations but rewrite the filename to the new versioned name.
    for row in existing_annotations:
        combined_annotations.append(
            {
                "file": combined_name,
                "line": int(row["line"]),
                "BeginOffset": int(row["BeginOffset"]),
                "EndOffset": int(row["EndOffset"]),
                "Type": row["Type"],
            }
        )

    # Append new annotations, shifting line numbers by the size of existing corpus.
    for row in new_annotations:
        combined_annotations.append(
            {
                "file": combined_name,
                "line": line_offset + int(row["line"]),
                "BeginOffset": int(row["BeginOffset"]),
                "EndOffset": int(row["EndOffset"]),
                "Type": row["Type"],
            }
        )

    return combined_lines, combined_annotations, combined_name, combined_annotation_name


def _split_dataset(
    combined_lines: List[str],
    combined_annotations: List[Dict],
    sample_fraction: float,
    combined_name: str,
) -> Tuple[List[str], List[Dict], List[str], List[Dict], int, int]:
    """Split the big file into analysis and training parts while keeping lines lined up."""
    total_lines = len(combined_lines)
    sample_count = int(total_lines * sample_fraction)
    # Make sure analysis gets at least one line but not the whole file.
    if sample_count < 1 and total_lines > 1:
        sample_count = 1
    if sample_count >= total_lines:
        sample_count = max(1, total_lines - 1)

    # Pick which lines belong to the analysis set.
    sampled_indices = set(random.sample(range(1, total_lines + 1), sample_count))
    logger.info("Sampling %s of %s lines for analysis", sample_count, total_lines)

    # Group annotations by the line they came from.
    annotations_by_line: Dict[int, List[Dict]] = {}
    for row in combined_annotations:
        annotations_by_line.setdefault(int(row["line"]), []).append(row)

    # Buckets for the analysis set and the training set.
    analysis_lines: List[str] = []
    train_lines: List[str] = []
    analysis_annotations: List[Dict] = []
    train_annotations: List[Dict] = []

    # Go through every line and send it to the analysis group or the training group.
    # Give each group its own line numbers and move any matching annotations to that new line.
    for idx, text in enumerate(combined_lines, start=1):
        if idx in sampled_indices:
            # Map old line index to new analysis line number.
            new_line_no = len(analysis_lines) + 1
            analysis_lines.append(text)
            for row in annotations_by_line.get(idx, []):
                analysis_annotations.append(
                    {
                        "file": combined_name,
                        "line": new_line_no,
                        "BeginOffset": row["BeginOffset"],
                        "EndOffset": row["EndOffset"],
                        "Type": row["Type"],
                    }
                )
        else:
            # Map old line index to new training line number.
            new_line_no = len(train_lines) + 1
            train_lines.append(text)
            for row in annotations_by_line.get(idx, []):
                train_annotations.append(
                    {
                        "file": combined_name,
                        "line": new_line_no,
                        "BeginOffset": row["BeginOffset"],
                        "EndOffset": row["EndOffset"],
                        "Type": row["Type"],
                    }
                )

    return analysis_lines, analysis_annotations, train_lines, train_annotations, sample_count, total_lines


def handler(event, context):
    try:
        # Folder prefixes and base names stay fixed.
        prepared_prefix = "prepared_data/"
        run_analysis_prefix = "run_analysis/"
        ready_to_train_prefix = "ready_to_train/"
        dataset_base_name = "training_doc"

        # Portion of data to hold out for evaluation.
        try:
            sample_fraction = float(get_env("SAMPLE_FRACTION", "0.1"))
        except ValueError as e:
            raise DataPreparationError("SAMPLE_FRACTION must be a float") from e

        # Fresh upload path: pull txt + csv passed via trigger.
        bucket, text_key, annotations_key = _extract_event_keys(event)
        logger.info("Preparing data from %s/%s and %s/%s", bucket, text_key, bucket, annotations_key)
        # Read and split the raw text by line to keep alignment with CSV lines.
        new_lines = _safe_load_text(bucket, text_key, "incoming text")
        # Parse CSV annotations.
        annotations = _load_annotations(bucket, annotations_key)

        # Make sure the CSV isn’t pointing at a text line that doesn’t exist.
        max_line = max((row["line"] for row in annotations), default=0)
        if max_line > len(new_lines):
            raise DataPreparationError(
                f"Annotations reference line {max_line} but text has only {len(new_lines)} lines"
            )

        # Load previous prepared data (if any)
        latest_version, latest_txt_key, latest_csv_key = _find_latest_version(
            bucket, prepared_prefix, dataset_base_name
        )

        # Start with empty history until we find one.
        existing_lines: List[str] = []
        existing_annotations: List[Dict] = []
        if latest_version > 0:
            logger.info("Found existing prepared set v%s", latest_version)
            # Bring forward last prepared text + annotations.
            existing_lines = _safe_load_text(bucket, latest_txt_key, "prepared text")
            existing_annotations = _load_annotations(bucket, latest_csv_key)

        # Combine old stuff with the new upload.
        next_version = latest_version + 1
        (
            combined_lines,
            combined_annotations,
            combined_name,
            combined_annotation_name,
        ) = _merge_datasets(
            existing_lines,
            existing_annotations,
            new_lines,
            annotations,
            dataset_base_name,
            next_version,
        )

        if not combined_lines:
            raise DataPreparationError("No training data found after merge")

        # Write merged prepared copy
        prepared_txt_key = f"{prepared_prefix}{combined_name}"
        prepared_csv_key = f"{prepared_prefix}{combined_annotation_name}"
        try:
            put_s3_text(bucket, prepared_txt_key, "\n".join(combined_lines))
            _write_csv(bucket, prepared_csv_key, combined_annotations)
        except (ClientError, BotoCoreError) as e:
            raise DataPreparationError(f"S3 error writing prepared artifacts: {e}") from e

        # Build run-analysis and ready-to-train splits.
        (
            analysis_lines,
            analysis_annotations,
            train_lines,
            train_annotations,
            sample_count,
            total_lines,
        ) = _split_dataset(combined_lines, combined_annotations, sample_fraction, combined_name)

        analysis_txt_key = f"{run_analysis_prefix}{combined_name}"
        analysis_csv_key = f"{run_analysis_prefix}{combined_annotation_name}"
        ready_txt_key = f"{ready_to_train_prefix}{combined_name}"
        ready_csv_key = f"{ready_to_train_prefix}{combined_annotation_name}"

        # Persist new splits for downstream steps.
        try:
            put_s3_text(bucket, analysis_txt_key, "\n".join(analysis_lines))
            _write_csv(bucket, analysis_csv_key, analysis_annotations)
            put_s3_text(bucket, ready_txt_key, "\n".join(train_lines))
            _write_csv(bucket, ready_csv_key, train_annotations)
        except (ClientError, BotoCoreError) as e:
            raise DataPreparationError(f"S3 error writing split artifacts: {e}") from e

        # Send back everything the next steps need.
        response = {
            "bucket": bucket,
            "dataset_version": next_version,
            "dataset_name": dataset_base_name,
            "prepared": {"text_key": prepared_txt_key, "annotations_key": prepared_csv_key},
            "run_analysis": {
                "text_key": analysis_txt_key,
                "annotations_key": analysis_csv_key,
                "line_count": len(analysis_lines),
            },
            "ready_to_train": {
                "text_key": ready_txt_key,
                "annotations_key": ready_csv_key,
                "line_count": len(train_lines),
            },
            "sample_fraction": sample_fraction,
            "total_lines": total_lines,
        }
        logger.info("Prepared dataset response: %s", json.dumps(response))
        return response
    except DataPreparationError:
        # We already know what went wrong, just log and rethrow.
        logger.exception("Data preparation failed due to input/validation error")
        raise
    except Exception as e:
        # Last-resort catch so the Step Function sees the failure.
        logger.exception("Data preparation failed unexpectedly")
        raise DataPreparationError(f"Unexpected failure: {e}") from e
