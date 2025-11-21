import csv
import io
import random
import re
from typing import Dict, List, Tuple

from botocore.exceptions import BotoCoreError, ClientError

from ..common import list_keys, load_s3_text, put_s3_text

FILE_COL = "File"
LINE_COL = "Line"
BEGIN_COL = "Begin Offset"
END_COL = "End Offset"
TYPE_COL = "Type"

REQUIRED_COLUMNS = [FILE_COL, LINE_COL, BEGIN_COL, END_COL, TYPE_COL]


class DataPreparationError(Exception):
    """Custom error so we know prep broke instead of the whole Lambda blowing up."""


def extract_event_keys(event: Dict) -> Tuple[str, str, str]:
    """Grab the bucket and both object keys from an S3 trigger (needs txt + csv)."""
    if "Records" in event:
        records = event["Records"]
        if len(records) < 2:
            raise ValueError("S3 trigger needs both the text file and the csv file")
        bucket = records[0]["s3"]["bucket"]["name"]
        keys = [r["s3"]["object"]["key"] for r in records]
        text_key = next((k for k in keys if k.lower().endswith(".txt")), None)
        csv_key = next((k for k in keys if k.lower().endswith(".csv")), None)
        if not text_key or not csv_key:
            raise ValueError("S3 trigger missing txt or csv payload")
        return bucket, text_key, csv_key

    raise ValueError("Unsupported event; expected S3 put with txt and csv")


def load_annotations(bucket: str, key: str) -> List[Dict]:
    """Read the CSV, check headers, and return rows as dicts."""
    raw = load_s3_text(bucket, key)
    try:
        reader = csv.DictReader(io.StringIO(raw))
    except csv.Error as e:
        raise DataPreparationError(f"Failed to read annotations CSV {bucket}/{key}: {e}") from e

    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise DataPreparationError(f"CSV missing required columns: {missing}")
    rows: List[Dict] = []
    for row in reader:
        rows.append(
            {
                FILE_COL: row[FILE_COL],
                LINE_COL: int(row[LINE_COL]),
                BEGIN_COL: int(row[BEGIN_COL]),
                END_COL: int(row[END_COL]),
                TYPE_COL: row[TYPE_COL],
            }
        )
    return rows


def write_csv(bucket: str, key: str, rows: List[Dict[str, str]]) -> None:
    """Dump rows back to CSV and upload to S3."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    try:
        put_s3_text(bucket, key, output.getvalue(), content_type="text/csv")
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"Failed to write CSV to {bucket}/{key}: {e}") from e


def safe_load_text(bucket: str, key: str, label: str) -> List[str]:
    """Pull a text file from S3 and split into lines, with friendlier errors."""
    try:
        return load_s3_text(bucket, key).splitlines()
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"S3 error loading {label} at {bucket}/{key}: {e}") from e
    except Exception as e:
        raise DataPreparationError(f"Unable to load {label} at {bucket}/{key}: {e}") from e


def find_latest_version(
    bucket: str, prefix: str, text_base: str, annotation_base: str
) -> Tuple[int, str, str]:
    """Look through S3 to find the highest version where both txt and csv exist."""
    try:
        keys = list_keys(bucket, prefix)
    except (ClientError, BotoCoreError) as e:
        raise DataPreparationError(f"S3 error listing {bucket}/{prefix}: {e}") from e

    text_pattern = re.compile(rf"{re.escape(prefix)}{re.escape(text_base)}_v(\d+)\.txt$")
    ann_pattern = re.compile(rf"{re.escape(prefix)}{re.escape(annotation_base)}_v(\d+)\.csv$")
    text_versions: Dict[int, str] = {}
    ann_versions: Dict[int, str] = {}

    for key in keys:
        tm = text_pattern.match(key)
        if tm:
            text_versions[int(tm.group(1))] = key
        am = ann_pattern.match(key)
        if am:
            ann_versions[int(am.group(1))] = key

    common_versions = set(text_versions) & set(ann_versions)
    if not common_versions:
        return 0, "", ""
    latest_version = max(common_versions)
    return latest_version, text_versions[latest_version], ann_versions[latest_version]


def merge_datasets(
    existing_lines: List[str],
    existing_annotations: List[Dict],
    new_lines: List[str],
    new_annotations: List[Dict],
    prepared_text_name: str,
    prepared_annotation_name: str,
) -> Tuple[List[str], List[Dict], str, str]:
    """Glue old and new data together and rewrite filenames to the new version."""
    combined_name = prepared_text_name
    combined_annotation_name = prepared_annotation_name

    # Add new lines after old lines.
    combined_lines = [*existing_lines, *new_lines]
    # Keep track so we can shift line numbers for the new chunk.
    line_offset = len(existing_lines)
    combined_annotations: List[Dict] = []

    # Copy old annotations but point them at the new combined file name.
    for row in existing_annotations:
        combined_annotations.append(
            {
                FILE_COL: combined_name,
                LINE_COL: int(row[LINE_COL]),
                BEGIN_COL: int(row[BEGIN_COL]),
                END_COL: int(row[END_COL]),
                TYPE_COL: row[TYPE_COL],
            }
        )

    # Now add new annotations, pushing their line numbers by the old length.
    for row in new_annotations:
        combined_annotations.append(
            {
                FILE_COL: combined_name,
                LINE_COL: line_offset + int(row[LINE_COL]),
                BEGIN_COL: int(row[BEGIN_COL]),
                END_COL: int(row[END_COL]),
                TYPE_COL: row[TYPE_COL],
            }
        )

    return combined_lines, combined_annotations, combined_name, combined_annotation_name


def split_dataset(
    combined_lines: List[str],
    combined_annotations: List[Dict],
    sample_fraction: float,
    process_analysis: bool,
    analysis_text_name: str,
    ready_text_name: str,
) -> Tuple[List[str], List[Dict], List[str], List[Dict], int, int]:
    """
    Split the big file into two parts:
    - analysis: the holdout chunk (only if process_analysis is true)
    - training: the rest
    Line numbers reset inside each split so CSV stays aligned.
    """
    total_lines = len(combined_lines)
    if not process_analysis:
        analysis_lines: List[str] = []
        analysis_annotations: List[Dict] = []
        train_lines = list(combined_lines)
        train_annotations = [
            {
                FILE_COL: ready_text_name,
                LINE_COL: int(row[LINE_COL]),
                BEGIN_COL: row[BEGIN_COL],
                END_COL: row[END_COL],
                TYPE_COL: row[TYPE_COL],
            }
            for row in combined_annotations
        ]
        return analysis_lines, analysis_annotations, train_lines, train_annotations, 0, total_lines

    sample_count = int(total_lines * sample_fraction)
    if sample_count < 1 and total_lines > 1:
        sample_count = 1
    if sample_count >= total_lines:
        sample_count = max(1, total_lines - 1)

    sampled_indices = set(random.sample(range(total_lines), sample_count))

    annotations_by_line: Dict[int, List[Dict]] = {}
    for row in combined_annotations:
        annotations_by_line.setdefault(int(row[LINE_COL]), []).append(row)

    analysis_lines: List[str] = []
    train_lines: List[str] = []
    analysis_annotations: List[Dict] = []
    train_annotations: List[Dict] = []

    for idx, text in enumerate(combined_lines):
        if idx in sampled_indices:
            new_line_no = len(analysis_lines)
            analysis_lines.append(text)
            for row in annotations_by_line.get(idx, []):
                analysis_annotations.append(
                    {
                        FILE_COL: analysis_text_name,
                        LINE_COL: new_line_no,
                        BEGIN_COL: row[BEGIN_COL],
                        END_COL: row[END_COL],
                        TYPE_COL: row[TYPE_COL],
                    }
                )
        else:
            new_line_no = len(train_lines)
            train_lines.append(text)
            for row in annotations_by_line.get(idx, []):
                train_annotations.append(
                    {
                        FILE_COL: ready_text_name,
                        LINE_COL: new_line_no,
                        BEGIN_COL: row[BEGIN_COL],
                        END_COL: row[END_COL],
                        TYPE_COL: row[TYPE_COL],
                    }
                )

    return analysis_lines, analysis_annotations, train_lines, train_annotations, sample_count, total_lines
