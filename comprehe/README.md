# Comprehend Custom Entity Training Pipeline

Enterprise-grade Step Functions workflow for preparing OFAC training data, training a Comprehend custom entity recognizer, running batch analysis, and evaluating results with automatic resampling when metrics regress.

## Architecture
- The draw.io diagram lives at `docs/architecture.drawio` (open in diagrams.net → File → Open and point at the file). It shows the S3-triggered Lambda that starts the state machine, every Step Functions task, Comprehend interactions, and where artifacts land in S3.
- High level: an S3 `training_docs/` upload triggers a small “start step function” Lambda, which kicks off the Step Functions pipeline. The pipeline prepares data, trains a custom recognizer, runs a batch analysis on the holdout set, evaluates metrics, and either succeeds or resamples and retries.

## Trigger flow
- **Upload format:** one `.zip` dropped into `training_docs/` containing exactly one `.txt` file (one line per document row) and one `.csv` of annotations.
- **Event path:** S3 event → `start_sf` Lambda (`infra/main.tf`) → Step Functions execution (`statemachine/definition.json`).
- **Manual start (optional):** `aws stepfunctions start-execution --state-machine-arn <arn> --input '{"bucket":"<bucket>","resample_only":true}'` can re-run the pipeline using the latest prepared version.

## State machine steps
- **DataPreparation (Lambda):** validates the zip, checks CSV headers, merges with the latest prepared dataset, versions outputs, and splits into `ready_to_train/` (90%) and `run_analysis/` (10%). Supports `resample_only=true` to just reshuffle the split.
- **TrainComprehend (Lambda):** calls `create_entity_recognizer` with entity types `FTO`, `OFAC ORG`, `OFAC POI`. Tries to warm-start from `BASE_ENTITY_RECOGNIZER` (via `list_entity_recognizers`) else `FALLBACK_ENTITY_RECOGNIZER_ARN`.
- **Wait 15m → GetTrainingStatus (Lambda):** polls until recognizer status is `TRAINED`; loops on `SUBMITTED`/`TRAINING`; fails on error states.
- **RunAnalysisJob (Lambda):** invokes `start_entities_detection_job` against the holdout split and points output to `analysis_output/`.
- **Wait 15m → GetAnalysisStatus (Lambda):** polls until job is `COMPLETED`; loops otherwise; fails on error states.
- **EvaluateResults (Lambda):** reads Comprehend output (tar.gz or JSON), compares to ground truth annotations, computes precision/recall/F1, writes `evaluation/metrics/<dataset>_vN.json`, and flags improvement versus the previous version.
- **ImprovementCheck:** if F1 improved, end with `Success`; if not, `ResampleRequest` re-enters `DataPreparation` with `resample_only=true` to reshuffle and retrain.

## S3 layout
- `training_docs/` – incoming zip uploads (one .txt + one .csv).
- `prepared_data/` – merged canonical dataset (e.g., `prepare_training_doc_v5.txt` + `_annotation_v5.csv`).
- `ready_to_train/` – training split per version.
- `run_analysis/` – holdout split per version.
- `analysis_output/` – Comprehend batch job output per version.
- `evaluation/metrics/` – per-version metrics JSON.

## Configuration (Lambda environment)
- `COMPREHEND_DATA_ACCESS_ROLE_ARN` – IAM role for Comprehend jobs (required).
- `ENTITY_RECOGNIZER_NAME` – recognizer name (default `custom-entity-recognizer`).
- `BASE_ENTITY_RECOGNIZER` – recognizer name to warm-start from (defaults to `ENTITY_RECOGNIZER_NAME`).
- `FALLBACK_ENTITY_RECOGNIZER_ARN` – static ARN if no base recognizer exists.
- `LANGUAGE_CODE` – default `en`.
- `SAMPLE_FRACTION` – holdout fraction (default `0.1`).
- `PROCESS_ANALYSIS` – `true` to create the holdout; `false` to send everything to training.
- Prefix overrides: `PREPARED_PREFIX`, `TRAINING_DOCS_PREFIX`, `RUN_ANALYSIS_PREFIX`, `READY_TO_TRAIN_PREFIX`, `ANALYSIS_OUTPUT_PREFIX`, `EVALUATION_METRICS_PREFIX`.

## Running end-to-end
- **Deploy:** Use your packaging/IaC to publish the task Lambdas plus the state machine. `infra/main.tf` shows how to wire the `start_sf` Lambda, training bucket notifications, and the state machine ARNs (pass your Lambda ARNs via `lambda_arns`).
- **Seed data:** Zip the sample inputs and upload to the training bucket:
  - `zip -j /tmp/ofac_sample.zip sample/ofac_sample.txt sample/ofac_annotations.csv`
  - `aws s3 cp /tmp/ofac_sample.zip s3://<training-bucket>/training_docs/ofac_sample.zip`
- **Observe:** Watch the execution in Step Functions (console or `aws stepfunctions describe-execution`). When complete, inspect:
  - `analysis_output/<dataset>_vN/...` for Comprehend predictions
  - `evaluation/metrics/<dataset>_vN.json` for metrics and the improvement flag
- **Resample-only run:** Start execution with `{ "bucket": "<bucket>", "resample_only": true }` to reshuffle the holdout without new uploads.

## CloudWatch logs & observability
- Each Lambda (including `start_sf`) writes to its own `/aws/lambda/<function-name>` log group.
- Step Functions execution history shows per-state inputs/outputs; enable execution logging if desired for payload traces.
- Comprehend training/analysis status is also visible via `aws comprehend describe-entity-recognizer` and `describe-entities-detection-job` using the ARNs/JobIds emitted by the pipeline.
- Metrics live in S3 (`evaluation/metrics/`); pull locally with `aws s3 cp s3://<bucket>/evaluation/metrics/<dataset>_vN.json -`.

## Debugging tips
- Zip payload must contain exactly one `.txt` and one `.csv` with headers `File, Line, Begin Offset, End Offset, Type` and UTF-8 encoding; otherwise `DataPreparation` raises `DataPreparationError`.
- If training never leaves `SUBMITTED/TRAINING`, check `COMPREHEND_DATA_ACCESS_ROLE_ARN` permissions and that input prefixes are correct.
- If evaluation fails to find predictions, confirm `analysis_output/` contains a `.tar.gz` (or NDJSON) file and the Lambda role can read it.
- Warm-start issues: ensure `BASE_ENTITY_RECOGNIZER` matches an existing recognizer name or set `FALLBACK_ENTITY_RECOGNIZER_ARN`.
- To iterate quickly, run with `PROCESS_ANALYSIS=false` to skip the holdout split, then re-enable once training is stable.

## Tests
- Local validation of the data prep flow: `python -m pytest tests/test_data_preparation.py` (uses moto to mock S3; no AWS calls are made).
