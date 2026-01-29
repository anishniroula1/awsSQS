"""
pipeline.py

Shared pipeline logic used by both:
- Lambda entrypoint (S3 mode): app.lambda_handler
- Local runner (no S3): run_local.py

If you want to test without S3, call `run_pipeline_from_files(...)`.
"""

from __future__ import annotations

import time
import logging
from typing import Any, Dict, List, Tuple, Optional

from s3io import read_json_file, read_jsonl_file, extract_comprehend_tar_gz
from matcher import build_phrase_index_from_csv, find_exact_matches, normalize_with_map
from comprehend_parser import to_lines_entities_json
from merge import merge_entities_for_sentence


def _norm_only(s: str) -> str:
    n, _ = normalize_with_map(s or "")
    return n


def _load_mapping_items(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("mappings", "items", "data"):
            if k in obj and isinstance(obj[k], list):
                return obj[k]
        if "Line" in obj:
            return [obj]
    raise ValueError("Mapping JSON must be a list (or wrapper containing a list).")


def _parse_mapping(obj: Any) -> Tuple[Dict[int, str], Dict[str, str], int]:
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


def run_pipeline_from_files(
    sanctions_csv_path: str,
    mapping_json_path: str,
    comprehend_tar_gz_path: str,
    *,
    sanctions_column: str = "sanction_list",
    max_candidates: int = 50_000,
    comprehend_tar_member: Optional[str] = None,
    extract_dir: str = "/tmp/comprehend_extract",
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """Run the full sanctions pipeline using local file paths (no S3 required)."""
    log = logger or logging.getLogger("sanctions-pipeline")
    t0 = time.time()

    mapping_obj = read_json_file(mapping_json_path)
    line_to_sid, sid_to_content, mapping_items_count = _parse_mapping(mapping_obj)

    jsonl_path = extract_comprehend_tar_gz(
        comprehend_tar_gz_path,
        extract_dir=extract_dir,
        preferred_member=comprehend_tar_member,
        logger=log,
    )
    log.info("Using extracted Comprehend JSONL file: %s", jsonl_path)

    comp_objs = read_jsonl_file(jsonl_path)
    comprehend_lines = to_lines_entities_json(comp_objs)

    comprehend_by_sentence: Dict[str, List[Dict[str, Any]]] = {}
    for i, line in enumerate(comprehend_lines, start=1):
        sid = line_to_sid.get(i)
        if not sid:
            continue
        comprehend_by_sentence.setdefault(sid, []).extend(line.get("entities") or [])

    phrases, anchor_index, _ = build_phrase_index_from_csv(
        sanctions_csv_path, column_name=sanctions_column, logger=log
    )
    sanction_norm_set = set(_norm_only(p.raw) for p in phrases if p.raw)

    csv_matches_by_id: Dict[str, List[Dict[str, Any]]] = {}
    total_csv_hits = 0
    for sid, text in sid_to_content.items():
        hits = find_exact_matches(text, phrases, anchor_index, max_candidates=max_candidates)
        if hits:
            csv_matches_by_id[sid] = hits
            total_csv_hits += len(hits)

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

    return {
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
            "maxCandidates": max_candidates,
            "tookMs": int((time.time() - t0) * 1000),
            "comprehendInputWasTarGz": True,
        },
    }
