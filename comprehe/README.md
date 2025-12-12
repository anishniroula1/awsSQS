# Student Essay Entity Extraction Pipeline

Pipeline that ingests SQS events, enriches student essays with AWS Comprehend (pre-trained and custom NER), stores structured entities in downstream services, and cleans up all intermediate S3 artifacts.

## High-Level Flow
- SQS (Ner queue) receives messages from the Python producer.
- Step Functions state machine executes three Lambdas in order: Data Prep → Job Status → Store Data.
- Data Prep fetches essays, builds S3 inputs, starts two Comprehend jobs, and returns job metadata.
- Job Status polls both jobs until success/failure (60s wait between checks).
- Store Data reads Comprehend outputs, merges entities (custom NER has priority), persists to APIs/DB, cleans S3, deletes the original SQS message, and emits a downstream SQS notification.

## Components
- **Producer**: Python app sends SQS message to Ner queue.
- **Step Function**: Orchestrates Lambdas with retry/backoff and status choices.
- **Lambda: Data Prep**: Input assembly, S3 writes, Comprehend submissions.
- **Lambda: Job Status**: Polls describe endpoints until terminal state.
- **Lambda: Store Data**: Reads outputs, merges/dedupes, calls APIs, performs cleanup.
- **AWS Comprehend**: Two jobs per student: pre-trained entity detection and custom entity recognizer.
- **S3**: Per-student working area for inputs and outputs.
- **Downstream APIs**: Essay fetch, bulk name entity insert, bulk sentence entity insert, student entity aggregation/update.
- **SQS (completion)**: Notification for the next service after DB writes succeed.

## S3 Contract
```
<bucket>/
  <student_id>/
    text/<student_id>.txt           # One essay per line; line index maps to essay_id via json file
    json/<student_id>.json          # [{"essay_id": 1, "line": 0}, ...]
    output/
      pre_trained/                  # Comprehend-managed prefix for pre-trained job output
      custom/                       # Comprehend-managed prefix for custom NER job output
```

## Message and Data Contracts
- **Inbound SQS message (from producer)** example:
  ```json
  {
    "message_id": "sqs-msg-id",        // keep receipt handle separately for delete
    "tsp_id": "trace-or-tenant-id",
    "student_id": "12345",
    "trigger_ts": "2024-12-10T09:41:00Z"
  }
  ```
- **Essays API response** (Data Prep uses this):
  ```json
  {
    "student_id": "12345",
    "essays": [
      {"essay_id": 1, "sentences": ["Sentence A.", "Sentence B."]},
      {"essay_id": 2, "sentences": ["Sentence C."]}
    ]
  }
  ```
- **Text file layout**: Each essay flattened to a single line (join sentences with spaces or keep as provided). Line number is stored in the JSON mapping file for reverse lookup.
- **Mapping JSON layout**: List of objects `{"essay_id": <id>, "line": <zero-based line number>}`.
- **Data Prep → Step Function output (state payload)**:
  ```json
  {
    "student_id": "12345",
    "message_id": "sqs-msg-id",
    "tsp_id": "trace-or-tenant-id",
    "s3_bucket": "bucket-name",
    "text_key": "12345/text/12345.txt",
    "mapping_key": "12345/json/12345.json",
    "comprehend": {
      "pretrained": {"job_id": "job-pre", "output_prefix": "12345/output/pre_trained/"},
      "custom": {"job_id": "job-custom", "output_prefix": "12345/output/custom/"}
    },
    "receipt_handle": "opaque-handle-for-delete"
  }
  ```
- **Comprehend outputs**: Gzipped JSON per job under the output prefixes, containing entities with `Text`, `Type`, `Score`, `BeginOffset`, `EndOffset`, and line index.

## Lambda Designs
### Data Prep
- Parse SQS event, extract `student_id`, `message_id`, `tsp_id`, and `receipt_handle`.
- Call Essays API to fetch essays and sentences for the student.
- Build files:
  - Text: one essay per line (line index is stable).
  - Mapping JSON: maps essay_id → line index for later reverse mapping.
- Upload files to S3 in the student namespace.
- Start two Comprehend jobs (pre-trained and custom) with:
  - Input: S3 URI of the text file.
  - Output prefixes: `.../output/pre_trained/` and `.../output/custom/`.
  - KMS and role ARNs supplied via env vars.
- Return state payload including job ids, S3 keys, message ids, tsp_id, and receipt handle.
- Fail fast on missing essays or upstream API errors; surface to Step Functions for retry/terminal handling.

### Job Status
- Describe both Comprehend jobs each invocation.
- If either job is `FAILED` or `STOPPED`, fail the state machine with details (and do not proceed).
- If both are `COMPLETED`, pass along job metadata and S3 prefixes.
- Otherwise wait 60 seconds (Step Functions Wait state) and re-check.
- Add retry with bounded attempts and exponential backoff on throttling/5xx from Comprehend.

### Store Data
- Download and parse both Comprehend outputs from S3.
- Entity precedence: if both jobs emit an entity for the same span/text, keep the custom NER version and drop the pre-trained one.
- Reverse-map line index → essay_id using the JSON mapping file.
- Build deduped Name Entities (unique by entity text + entity type); reuse existing IDs if API returns matches.
- Build Sentence Entities:
  - Fields: essay_id, student_id, sentence text, name_entity_id, begin_offset, end_offset, score, model_type.
  - One sentence may produce multiple entity rows.
- Build Student Entity aggregates:
  - Count occurrences of each name entity per student across essays.
  - Upsert counts (incremental).
- Call downstream APIs in order: bulk insert name entities → bulk insert sentence entities → bulk upsert student entity counts.
- On success:
  - Delete the entire `student_id` prefix in S3 (inputs and outputs).
  - Delete the original SQS message using the receipt handle.
  - Emit completion SQS event for the next service.
- On failure:
  - Do not delete S3; let reruns inspect artifacts.
  - Propagate error so Step Functions can route to DLQ/alerting.

## State Machine Design
- **States**:
  - `DataPrep` (Task, retry on transient errors).
  - `JobStatus` (Task) → `Wait60s` (Wait) → loop until terminal state.
  - Choice: if status success → `StoreData`; else → `Fail` with reason.
  - Terminal: `Success` or `Failure`.
- **Retries**: Configure per state for throttling/5xx with backoff; cap attempts to avoid runaway cost.
- **Timeouts**: Per-task timeout to avoid stuck executions; Comprehend jobs also have max runtime watchdog.

## Database and API Notes
- **Tables**:
  - Name Entity: unique (entity_text, entity_type); returns id for reuse.
  - Sentence Entity: essay_id, student_id, sentence, name_entity_id, begin_offset, end_offset, score, model_type, tsp_id, job_ids.
  - Student Entity: student_id, name_entity_id, total_count.
- **APIs**:
  - `POST /name-entities/bulk` → returns existing/new ids per (text, type).
  - `POST /sentence-entities/bulk` → create rows.
  - `POST /student-entities/bulk-upsert` → increment or set counts.
  - `GET /students/{id}/essays` → fetch essays/sentences.
- Include `message_id`, `tsp_id`, and job ids in payloads for traceability.

## Error Handling and Idempotency
- Use DLQ on the input SQS queue; send Step Functions failures to an alerting topic.
- Idempotency keys:
  - S3 prefixes scoped by student_id; overwrite-safe for reruns.
  - Dedup name entities by text+type; sentence entities dedup by (essay_id, entity span, model_type).
  - Avoid deleting S3 or SQS message on partial failures; only after full success.
- Guardrails:
  - Validate required fields in the inbound SQS message.
  - Short-circuit if essay list is empty.
  - Detect mismatched line mappings; fail with context.

## Security, Observability, Ops
- Encrypt S3 with SSE-KMS; restrict bucket to required IAM principals.
- Comprehend jobs configured with KMS for input/output.
- Principle of least privilege on Lambda roles and Comprehend service roles.
- Logging: structured JSON with student_id, message_id, tsp_id, job_id; emit counts of entities per model.
- Metrics/alerts: job failures, retries, latency per state, number of entities stored, S3 cleanup success.
- Tracing: enable X-Ray on Lambdas and Step Functions; propagate trace ids in API calls.

## Configuration
- Environment variables: bucket name, Comprehend role ARN, KMS key ids, API base URLs/keys, output prefixes, wait seconds (default 60), max poll attempts, completion SQS queue URL.
- Feature flags: toggle custom model usage; toggle cleanup for debugging.

## Edge Cases to Handle
- Very large essays: enforce size limits before Comprehend submission.
- Empty or malformed Comprehend output: fail gracefully and retain artifacts.
- Partial API availability: retry with backoff; ensure bulk operations are chunked to avoid payload limits.
- Duplicate students in rapid succession: ensure prefix and idempotency keys avoid collisions.

## Verification Checklist
- Unit tests for mapping logic (essay_id ↔ line index) and entity precedence.
- Contract tests for API payloads (bulk name/sentence/student entities).
- Integration test stub that runs Data Prep end-to-end with mocked Comprehend outputs.
- Manual runbook: replay DLQ message, inspect S3 artifacts, rerun Store Data with preserved inputs.

## Repo Layout (code)
- `src/data_prep/handler.py`: builds S3 inputs and starts Comprehend jobs.
- `src/job_status/handler.py`: polls Comprehend until completion/failure.
- `src/store_data/handler.py`: merges outputs, calls APIs, cleans up S3/SQS, and emits the completion event.
- `src/common/*`: shared config, Comprehend helpers, S3 helpers, and API client.
- `template.yaml`: SAM template wiring Lambdas and the state machine.
- `statemachine.asl.json`: Step Functions definition referenced by SAM.

## Required Environment Variables
- `BUCKET_NAME`
- `ESSAY_API_URL` (e.g., `https://.../students`)
- `NAME_ENTITY_BULK_URL`, `SENTENCE_ENTITY_BULK_URL`, `STUDENT_ENTITY_BULK_URL`
- `SOURCE_QUEUE_URL` (original SQS queue for delete)
- `COMPLETION_QUEUE_URL` (downstream notification queue)
- `COMPREHEND_ROLE_ARN`, `CUSTOM_RECOGNIZER_ARN`, `KMS_KEY_ID`, `LANGUAGE_CODE` (default `en`)
- `API_KEY` if your APIs need one
- `WAIT_SECONDS` (default `60`), `CLEANUP_ENABLED` (default `true`), `FEATURE_FLAG_CUSTOM_MODEL` (default `true`)

## Deploying with AWS SAM (example)
```
sam build
sam deploy \
  --stack-name student-entity-pipeline \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    BucketName=my-bucket \
    EssayApiUrl=https://api.example.com/students \
    NameEntityBulkUrl=https://api.example.com/name-entities/bulk \
    SentenceEntityBulkUrl=https://api.example.com/sentence-entities/bulk \
    StudentEntityBulkUrl=https://api.example.com/student-entities/bulk \
    SourceQueueUrl=https://sqs.us-east-1.amazonaws.com/123/source \
    CompletionQueueUrl=https://sqs.us-east-1.amazonaws.com/123/completion \
    ComprehendRoleArn=arn:aws:iam::123:role/comprehend-access \
    CustomRecognizerArn=arn:aws:comprehend:us-east-1:123:entity-recognizer/custom \
    KmsKeyId=arn:aws:kms:us-east-1:123:key/abc \
    ApiKey=my-api-key
```
