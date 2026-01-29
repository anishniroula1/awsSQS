"""
run_local.py

Run the pipeline locally using file paths (no S3).

Example:
  python run_local.py --sanctions-csv sanctions.csv --mapping-json mapping.json --comprehend-tar output.tar.gz --out final.json
"""

from __future__ import annotations

import argparse
import json
import logging
from pipeline import run_pipeline_from_files


def _configure_logger(verbose: bool) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    return logging.getLogger("sanctions-local")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run sanctions pipeline locally (no S3).")
    p.add_argument("--sanctions-csv", required=True)
    p.add_argument("--mapping-json", required=True)
    p.add_argument("--comprehend-tar", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sanctions-column", default="sanction_list")
    p.add_argument("--max-candidates", type=int, default=50000)
    p.add_argument("--comprehend-tar-member", default=None)
    p.add_argument("--extract-dir", default="/tmp/comprehend_extract")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    log = _configure_logger(args.verbose)

    payload = run_pipeline_from_files(
        sanctions_csv_path=args.sanctions_csv,
        mapping_json_path=args.mapping_json,
        comprehend_tar_gz_path=args.comprehend_tar,
        sanctions_column=args.sanctions_column,
        max_candidates=args.max_candidates,
        comprehend_tar_member=args.comprehend_tar_member,
        extract_dir=args.extract_dir,
        logger=log,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    log.info("Wrote output: %s", args.out)
    log.info("Meta: %s", payload.get("meta"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
