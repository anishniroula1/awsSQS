"""
app.py (AWS Lambda)

This Lambda does NOT download "sentences.json".
Sentences come from your upstream API response, which you store in S3 as a mapping JSON with items like:
  {"Line": 1, "content": "...", "sentence_id": "..."}

This Lambda downloads ONLY:
- Sanctions CSV from S3
- Comprehend JSONL from S3
- Mapping JSON from S3 (Line -> sentence_id + content)

Pipeline:
1) Convert Comprehend JSONL -> normalized JSON structure: [{lineNumber, entities:[...]}]
2) Join Comprehend lineNumber -> sentence_id using mapping
3) Run CSV->sentence exact matching on mapping.content (offsets are in that content)
4) Merge entities and set sanctionFlag=true when sanctioned
5) Deduplicate records (same span + same normalized text)
6) Optionally write final JSON back to S3

Handler: app.lambda_handler
"""

from __future__ import annotations

import os
import time
import logging
from typing import Any, Dict, List, Tuple

from s3io import download_to_tmp, read_json_file, read_jsonl_file, upload_json
from matcher import build_phrase_index_from_csv, find_exact_matches, normalize_with_map
from comprehend_parser import to_lines_entities_json
from merge import merge_entities_for_sentence


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


def _norm_only(s: str) -> str:
    n, _ = normalize_with_map(s or "")
    return n


def _load_mapping_items(obj: Any) -> List[Dict[str, Any]]:
    """Accept a list of mapping objects or a wrapper containing a list."""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("mappings", "items", "data"):
            if k in obj and isinstance(obj[k], list):
                return obj[k]
        if "Line" in obj and ("sentence_id" in obj or "sentenceId" in obj or "id" in obj):
            return [obj]
    raise ValueError("Mapping JSON must be a list (or wrapper containing a list).")


def _parse_mapping(obj: Any) -> Tuple[Dict[int, str], Dict[str, str], int]:
    """
    Returns:
      line_to_sentence_id: {1: "S0001", ...}
      sentence_to_content: {"S0001": "...", ...}
      total_items: count (from the file, not filtered)
    """
    items = _load_mapping_items(obj)
    line_to_sid: Dict[int, str] = {}
    sid_to_content: Dict[str, str] = {}

    for it in items:
        if not isinstance(it, dict):
            continue
        line = it.get("Line") if it.get("Line") is not None else it.get("line")
        sid = it.get("sentence_id") or it.get("sentenceId") or it.get("id")
        content = it.get("content")

        if line is None or sid is None or content is None:
            continue

        try:
            line_i = int(line)
        except Exception:
            continue

        sid_s = str(sid)
        line_to_sid[line_i] = sid_s
        sid_to_content[sid_s] = str(content)

    return line_to_sid, sid_to_content, len(items)


def lambda_handler(event, context):
    log = _configure_logger()
    t0 = time.time()

    # Required env vars
    sanctions_bucket = _getenv("SANCTIONS_BUCKET")
    sanctions_key = _getenv("SANCTIONS_KEY")
    sanctions_col = _getenv("SANCTIONS_COLUMN", "sanction_list")

    comprehend_bucket = _getenv("COMPREHEND_BUCKET")
    comprehend_key = _getenv("COMPREHEND_KEY")

    mapping_bucket = _getenv("MAPPING_BUCKET")
    mapping_key = _getenv("MAPPING_KEY")

    # Optional output
    output_bucket = os.getenv("OUTPUT_BUCKET")
    output_key = os.getenv("OUTPUT_KEY")

    max_candidates = int(_getenv("MAX_CANDIDATES", "50000"))
    preview_n = int(os.getenv("PREVIEW_N", "3"))

    # Download inputs
    sanctions_path = download_to_tmp(sanctions_bucket, sanctions_key, "sanctions.csv", logger=log)
    mapping_path = download_to_tmp(mapping_bucket, mapping_key, "mapping.json", logger=log)
    comprehend_path = download_to_tmp(comprehend_bucket, comprehend_key, "comprehend.jsonl", logger=log)

    # Load mapping (sentences source)
    log.info("Loading mapping JSON (source of sentence text)...")
    mapping_obj = read_json_file(mapping_path)
    line_to_sid, sid_to_content, mapping_items_count = _parse_mapping(mapping_obj)
    log.info("Mapping: items=%d line_to_sid=%d unique_sentences=%d",
             mapping_items_count, len(line_to_sid), len(sid_to_content))

    # Load & convert Comprehend JSONL
    log.info("Loading Comprehend JSONL...")
    comp_objs = read_jsonl_file(comprehend_path)
    log.info("Loaded %d JSONL lines", len(comp_objs))

    log.info("Converting Comprehend JSONL -> normalized JSON structure...")
    comprehend_lines = to_lines_entities_json(comp_objs)

    # Join lineNumber -> sentence_id and group entities by sentence_id
    comprehend_by_sentence: Dict[str, List[Dict[str, Any]]] = {}
    for i, line in enumerate(comprehend_lines, start=1):
        sid = line_to_sid.get(i)
        if not sid:
            continue
        ents = line.get("entities") or []
        comprehend_by_sentence.setdefault(sid, []).extend(ents)
    log.info("Comprehend grouped into %d sentences", len(comprehend_by_sentence))

    # Build sanctions index
    log.info("Building sanctions index from CSV...")
    phrases, anchor_index, _ = build_phrase_index_from_csv(sanctions_path, column_name=sanctions_col, logger=log)
    sanction_norm_set = set(_norm_only(p.raw) for p in phrases if p.raw)
    log.info("Sanctions normalized set size=%d", len(sanction_norm_set))

    # CSV->sentence scan using mapping.content
    log.info("Scanning sentences for CSV sanction hits (exact)...")
    csv_matches_by_id: Dict[str, List[Dict[str, Any]]] = {}
    total_csv_hits = 0

    for sid, text in sid_to_content.items():
        hits = find_exact_matches(text, phrases, anchor_index, max_candidates=max_candidates)
        if hits:
            csv_matches_by_id[sid] = hits
            total_csv_hits += len(hits)

    log.info("CSV hits: sentences_with_hits=%d total_hits=%d", len(csv_matches_by_id), total_csv_hits)

    # Merge
    log.info("Merging CSV hits + Comprehend entities...")
    final_results = []
    total_entities = 0
    sanctioned_entities = 0

    for sid, text in sid_to_content.items():
        merged = merge_entities_for_sentence(
            sentence_text=text,
            csv_matches=csv_matches_by_id.get(sid, []),
            comprehend_entities=comprehend_by_sentence.get(sid, []),
            sanction_norm_set=sanction_norm_set,
        )
        if merged:
            total_entities += len(merged)
            sanctioned_entities += sum(1 for e in merged if e.get("sanctionFlag"))
            final_results.append({"sentence_id": sid, "content": text, "entities": merged})

    payload = {
        "results": final_results,
        "meta": {
            "mappingItems": mapping_items_count,
            "uniqueSentences": len(sid_to_content),
            "comprehendLines": len(comp_objs),
            "sanctionsEntitiesLoaded": len(phrases),
            "csvSentenceHitCount": total_csv_hits,
            "sentencesWithCsvHits": len(csv_matches_by_id),
            "sentencesWithEntities": len(final_results),
            "totalEntities": total_entities,
            "sanctionedEntities": sanctioned_entities,
            "tookMs": int((time.time() - t0) * 1000),
        },
    }

    if output_bucket and output_key:
        upload_json(output_bucket, output_key, payload, logger=log)

    return {
        "meta": payload["meta"],
        "preview": payload["results"][:preview_n],
        "outputWritten": bool(output_bucket and output_key),
    }
