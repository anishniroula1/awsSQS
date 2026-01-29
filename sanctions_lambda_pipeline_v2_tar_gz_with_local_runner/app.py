"""app.py (AWS Lambda entrypoint, S3-based)."""

from __future__ import annotations

import os
import logging
from s3io import download_to_tmp, upload_json
from pipeline import run_pipeline_from_files


def _getenv(name: str, default: str | None = None) -> str:
    v = os.getenv(name)
    if (v is None or v == "") and default is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v if v not in (None, "") else str(default)


def _configure_logger() -> logging.Logger:
    log = logging.getLogger("sanctions-lambda")
    if not log.handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    return log


def lambda_handler(event, context):
    log = _configure_logger()

    sanctions_bucket = _getenv("SANCTIONS_BUCKET")
    sanctions_key = _getenv("SANCTIONS_KEY")
    sanctions_col = _getenv("SANCTIONS_COLUMN", "sanction_list")

    comprehend_bucket = _getenv("COMPREHEND_BUCKET")
    comprehend_key = _getenv("COMPREHEND_KEY")

    mapping_bucket = _getenv("MAPPING_BUCKET")
    mapping_key = _getenv("MAPPING_KEY")

    output_bucket = os.getenv("OUTPUT_BUCKET")
    output_key = os.getenv("OUTPUT_KEY")

    max_candidates = int(_getenv("MAX_CANDIDATES", "50000"))
    preview_n = int(os.getenv("PREVIEW_N", "3"))
    tar_member = os.getenv("COMPREHEND_TAR_MEMBER") or None

    sanctions_path = download_to_tmp(sanctions_bucket, sanctions_key, "sanctions.csv", logger=log)
    mapping_path = download_to_tmp(mapping_bucket, mapping_key, "mapping.json", logger=log)
    tar_path = download_to_tmp(comprehend_bucket, comprehend_key, "output.tar.gz", logger=log)

    payload = run_pipeline_from_files(
        sanctions_csv_path=sanctions_path,
        mapping_json_path=mapping_path,
        comprehend_tar_gz_path=tar_path,
        sanctions_column=sanctions_col,
        max_candidates=max_candidates,
        comprehend_tar_member=tar_member,
        logger=log,
    )

    if output_bucket and output_key:
        upload_json(output_bucket, output_key, payload, logger=log)

    return {
        "meta": payload["meta"],
        "preview": payload["results"][:preview_n],
        "outputWritten": bool(output_bucket and output_key),
    }
