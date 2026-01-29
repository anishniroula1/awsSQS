# Sanctions + Comprehend Lambda (Exact) — Mapping-Driven Sentences

This Lambda version **does not download sentences JSON**.

Your upstream API response is stored in S3 as a mapping JSON with items like:
```json
{"Line": 1, "content": "....", "sentence_id": "S0001"}
```

## Downloads from S3
- Sanctions CSV (`SANCTIONS_BUCKET`, `SANCTIONS_KEY`)
- Comprehend JSONL (`COMPREHEND_BUCKET`, `COMPREHEND_KEY`)
- Mapping JSON (`MAPPING_BUCKET`, `MAPPING_KEY`) — contains sentence text

## What it does
- Converts Comprehend JSONL -> normalized JSON: `[{lineNumber, entities:[...]}]`
- Joins Comprehend lineNumber -> sentence_id using mapping
- Runs CSV->sentence exact matching on `mapping.content` (offsets are on that content)
- Merges CSV hits + Comprehend entities
- Adds `sanctionFlag=true` when sanctioned
- Dedupes entities (same span + same normalized text)
- Optionally writes output JSON to S3

## Handler
Set handler to:
- `app.lambda_handler`

## Required environment variables
- `SANCTIONS_BUCKET`, `SANCTIONS_KEY`
- `COMPREHEND_BUCKET`, `COMPREHEND_KEY`
- `MAPPING_BUCKET`, `MAPPING_KEY`

Optional:
- `SANCTIONS_COLUMN` (default `sanction_list`)
- `MAX_CANDIDATES` (default `50000`)
- `OUTPUT_BUCKET`, `OUTPUT_KEY`
- `PREVIEW_N` (default `3`)
