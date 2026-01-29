# Sanctions + Comprehend Pipeline (Exact) — S3 + Local runner

This package supports **two ways** to run the same pipeline:

1) **AWS Lambda (S3 mode)**: `app.lambda_handler`
2) **Local files (no S3)**: `python run_local.py ...`

Inputs:
- Sanctions CSV (semicolon-separated entities in one column)
- Mapping JSON: `[{ "Line": 1, "content": "...", "sentence_id": "..." }, ...]`
- Comprehend output: **output.tar.gz** (member files may have no extension; inside is JSONL)

## Local run (no S3)
```bash
pip install -r requirements-dev.txt

python run_local.py   --sanctions-csv ./sanctions.csv   --mapping-json ./mapping.json   --comprehend-tar ./output.tar.gz   --out ./final.json
```

Optional flags:
- `--sanctions-column sanction_list`
- `--max-candidates 50000`
- `--comprehend-tar-member part-00000`  (skip auto-detect)
- `--extract-dir /tmp/comprehend_extract`

## Lambda run (S3 mode)
Env vars:
- `SANCTIONS_BUCKET`, `SANCTIONS_KEY`
- `MAPPING_BUCKET`, `MAPPING_KEY`
- `COMPREHEND_BUCKET`, `COMPREHEND_KEY`  (tar.gz key)
Optional:
- `COMPREHEND_TAR_MEMBER`
- `OUTPUT_BUCKET`, `OUTPUT_KEY`
