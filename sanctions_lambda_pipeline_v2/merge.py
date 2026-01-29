"""
merge.py

Merges:
1) CSV->Sentence matches (exact scanning; sanctioned by definition)
2) Comprehend entities

Rules:
- CSV matches => sanctionFlag=True
- Comprehend entity overlaps CSV span => sanctionFlag=True (+ sanctionEntity from CSV)
- Else, Comprehend entity is sanctioned if normalized text exists in sanctions set
- Deduplicate by (beginOffset, endOffset, normalized_text) and union sources
"""

from __future__ import annotations

from typing import Dict, List, Any, Tuple, Optional, Set
from matcher import normalize_with_map

def _normalize_only(text: str) -> str:
    norm, _ = normalize_with_map(text or "")
    return norm

def spans_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end

def merge_entities_for_sentence(sentence_text: str, csv_matches: List[Dict[str, Any]], comprehend_entities: List[Dict[str, Any]], sanction_norm_set: Set[str]) -> List[Dict[str, Any]]:
    merged: Dict[Tuple[int, int, str], Dict[str, Any]] = {}

    def upsert(rec: Dict[str, Any]) -> None:
        key = (rec["beginOffset"], rec["endOffset"], _normalize_only(rec["text"]))
        existing = merged.get(key)
        if not existing:
            merged[key] = rec
            return
        existing["sources"] = sorted(set(existing["sources"]) | set(rec["sources"]))
        existing["sanctionFlag"] = bool(existing.get("sanctionFlag") or rec.get("sanctionFlag"))
        if rec.get("sanctionEntity"):
            if not existing.get("sanctionEntity") or len(str(rec["sanctionEntity"])) > len(str(existing["sanctionEntity"])):
                existing["sanctionEntity"] = rec["sanctionEntity"]
        for k in ("type", "score"):
            if k in rec and k not in existing:
                existing[k] = rec[k]

    csv_spans = []
    for m in csv_matches:
        b, e = int(m["beginOffset"]), int(m["endOffset"])
        csv_spans.append((b, e, m["entity"]))
        upsert({
            "text": m.get("matchedText", sentence_text[b:e]),
            "beginOffset": b,
            "endOffset": e,
            "sources": ["csv_sentence_match"],
            "sanctionFlag": True,
            "sanctionEntity": m["entity"],
        })

    for ent in comprehend_entities:
        text = ent.get("Text") or ""
        b = ent.get("BeginOffset")
        e = ent.get("EndOffset")
        try:
            b = int(b)
            e = int(e)
        except Exception:
            continue
        if not text or b < 0 or e <= b:
            continue

        overlap_name: Optional[str] = None
        for cb, ce, cname in csv_spans:
            if spans_overlap(b, e, cb, ce):
                overlap_name = cname
                break

        sanction_flag = False
        sanction_entity: Optional[str] = None
        if overlap_name:
            sanction_flag = True
            sanction_entity = overlap_name
        else:
            norm = _normalize_only(text)
            if norm and norm in sanction_norm_set:
                sanction_flag = True
                sanction_entity = text

        rec = {
            "text": text,
            "beginOffset": b,
            "endOffset": e,
            "sources": ["comprehend"],
            "sanctionFlag": sanction_flag,
            "type": ent.get("Type"),
            "score": ent.get("Score"),
        }
        if sanction_entity:
            rec["sanctionEntity"] = sanction_entity
        upsert(rec)

    out = list(merged.values())
    out.sort(key=lambda r: (r["beginOffset"], -(r["endOffset"] - r["beginOffset"])))
    return out
