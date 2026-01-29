"""
comprehend_parser.py

Converts Comprehend JSONL -> normalized JSON structure:
  [{"lineNumber": 1, "entities": [ {Text, BeginOffset, EndOffset, Type, Score}, ... ]}, ...]

Tolerant parser:
- looks for Entities/entities directly or under Result/Output/Response nesting
- if a line is itself a list of dicts, treats it as the entities list
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

def _dig_for_entities(obj: Any) -> Optional[List[Dict[str, Any]]]:
    if obj is None:
        return None
    if isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return obj  # type: ignore
        return None
    if not isinstance(obj, dict):
        return None

    for k in ("Entities", "entities", "EntityList", "entityList"):
        if k in obj and isinstance(obj[k], list):
            return obj[k]  # type: ignore

    for k in ("Result", "result", "Response", "response", "Output", "output"):
        if k in obj:
            found = _dig_for_entities(obj[k])
            if found is not None:
                return found
    return None

def to_lines_entities_json(objs: List[Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, obj in enumerate(objs, start=1):
        ents = _dig_for_entities(obj) or []
        norm_ents = []
        for e in ents:
            if not isinstance(e, dict):
                continue
            norm_ents.append({
                "Text": e.get("Text") or e.get("text"),
                "BeginOffset": e.get("BeginOffset") if e.get("BeginOffset") is not None else e.get("beginOffset"),
                "EndOffset": e.get("EndOffset") if e.get("EndOffset") is not None else e.get("endOffset"),
                "Type": e.get("Type") or e.get("type"),
                "Score": e.get("Score") if e.get("Score") is not None else e.get("score"),
            })
        out.append({"lineNumber": i, "entities": norm_ents})
    return out
