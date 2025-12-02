import json
from dataclasses import dataclass
from typing import Dict, List

from botocore.exceptions import BotoCoreError, ClientError

from common import get_env, put_s3_text
from data_prep.utils import (
    FILE_COL,
    LINE_COL,
    BEGIN_COL,
    END_COL,
    TYPE_COL,
    DataPreparationError,
    extract_event_keys,
    find_latest_version,
    load_annotations,
    merge_datasets,
    safe_load_text,
    split_dataset,
    write_csv,
)


@dataclass
class DataPrepConfig:
    """Simple bag of settings so we can tweak names and split rules."""
    prepared_prefix: str = "prepared_data/"
    run_analysis_prefix: str = "run_analysis/"
    ready_to_train_prefix: str = "ready_to_train/"
    prepared_text_base: str = "prepare_training_doc"
    prepared_annotation_base: str = "prepare_annotation"
    analysis_text_base: str = "analysis_training_doc"
    analysis_annotation_base: str = "analysis_annotation"
    ready_text_base: str = "train_training_doc"
    ready_annotation_base: str = "train_annotation"
    sample_fraction: float = 0.1
    process_analysis: bool = True


class DataPreparationService:
    def __init__(self, config: DataPrepConfig):
        """Store the config we will use for all steps."""
        self.cfg = config

    def process(self, event: Dict) -> Dict:
        """Take an S3 event, merge data, split it, and return all S3 keys."""
        bucket, new_lines, annotations = extract_event_keys(event)

        # Make sure the CSV never points past the text length (zero-based lines).
        max_line = max((row[LINE_COL] for row in annotations), default=-1)
        if max_line >= len(new_lines):
            raise DataPreparationError(
                f"Annotations reference line {max_line} but text has only {len(new_lines)} lines"
            )

        latest_version, latest_txt_key, latest_csv_key = find_latest_version(
            bucket,
            self.cfg.prepared_prefix,
            self.cfg.prepared_text_base,
            self.cfg.prepared_annotation_base,
        )

        # Load the last prepared set so we can append.
        existing_lines: List[str] = []
        existing_annotations: List[Dict] = []
        if latest_version > 0:
            existing_lines = safe_load_text(bucket, latest_txt_key, "prepared text")
            existing_annotations = load_annotations(bucket, latest_csv_key)

        # Build new version names.
        next_version = latest_version + 1
        prepared_text_name = f"{self.cfg.prepared_text_base}_v{next_version}.txt"
        prepared_annotation_name = f"{self.cfg.prepared_annotation_base}_v{next_version}.csv"
        combined_lines, combined_annotations, combined_name, combined_annotation_name = merge_datasets(
            existing_lines,
            existing_annotations,
            new_lines,
            annotations,
            prepared_text_name,
            prepared_annotation_name,
        )

        if not combined_lines:
            raise DataPreparationError("No training data found after merge")

        # Save the merged (master) copy.
        prepared_txt_key = f"{self.cfg.prepared_prefix}{combined_name}"
        prepared_csv_key = f"{self.cfg.prepared_prefix}{combined_annotation_name}"
        try:
            put_s3_text(bucket, prepared_txt_key, "\n".join(combined_lines))
            write_csv(bucket, prepared_csv_key, combined_annotations)
        except (ClientError, BotoCoreError) as e:
            raise DataPreparationError(f"S3 error writing prepared artifacts: {e}") from e

        # Build names for the split outputs.
        analysis_text_name = f"{self.cfg.analysis_text_base}_v{next_version}.txt"
        analysis_annotation_name = f"{self.cfg.analysis_annotation_base}_v{next_version}.csv"
        ready_text_name = f"{self.cfg.ready_text_base}_v{next_version}.txt"
        ready_annotation_name = f"{self.cfg.ready_annotation_base}_v{next_version}.csv"

        (
            analysis_lines,
            analysis_annotations,
            train_lines,
            train_annotations,
            sample_count,
            total_lines,
        ) = split_dataset(
            combined_lines,
            combined_annotations,
            self.cfg.sample_fraction,
            self.cfg.process_analysis,
            analysis_text_name,
            ready_text_name,
        )

        analysis_txt_key = f"{self.cfg.run_analysis_prefix}{analysis_text_name}"
        analysis_csv_key = f"{self.cfg.run_analysis_prefix}{analysis_annotation_name}"
        ready_txt_key = f"{self.cfg.ready_to_train_prefix}{ready_text_name}"
        ready_csv_key = f"{self.cfg.ready_to_train_prefix}{ready_annotation_name}"

        # Save both splits.
        try:
            put_s3_text(bucket, analysis_txt_key, "\n".join(analysis_lines))
            write_csv(bucket, analysis_csv_key, analysis_annotations)
            put_s3_text(bucket, ready_txt_key, "\n".join(train_lines))
            write_csv(bucket, ready_csv_key, train_annotations)
        except (ClientError, BotoCoreError) as e:
            raise DataPreparationError(f"S3 error writing split artifacts: {e}") from e

        return {
            "bucket": bucket,
            "dataset_version": next_version,
            "dataset_name": self.cfg.prepared_text_base,
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
            "sample_fraction": self.cfg.sample_fraction if self.cfg.process_analysis else 0.0,
            "process_analysis": self.cfg.process_analysis,
            "total_lines": total_lines,
        }

    @staticmethod
    def from_env() -> "DataPreparationService":
        sample_fraction = 0.1
        try:
            sample_fraction = float(get_env("SAMPLE_FRACTION", "0.1"))
        except ValueError as e:
            raise DataPreparationError("SAMPLE_FRACTION must be a float") from e

        process_analysis = get_env("PROCESS_ANALYSIS", "true").lower() == "true"

        cfg = DataPrepConfig(
            sample_fraction=sample_fraction,
            process_analysis=process_analysis,
        )
        return DataPreparationService(cfg)
