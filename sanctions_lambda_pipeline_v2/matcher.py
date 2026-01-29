"""
matcher.py

Exact entity matching (sanctions entities) against sentence content with begin/end offsets.

Exact is "exact under normalization":
- lowercase
- keep alphanumeric
- normalize other chars to spaces
- collapse spaces

This makes matching tolerant of punctuation/case differences.
"""

from __future__ import annotations

import csv
import re
import time
import logging
from dataclasses import dataclass
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set, Any

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)

@dataclass(frozen=True)
class Phrase:
    raw: str
    norm: str
    toks: Tuple[str, ...]

def normalize_with_map(s: str) -> Tuple[str, List[int]]:
    norm_chars: List[str] = []
    idx_map: List[int] = []
    prev_space = False

    for i, ch in enumerate(s):
        c = ch.lower()
        if c.isalnum():
            norm_chars.append(c)
            idx_map.append(i)
            prev_space = False
        else:
            if norm_chars and not prev_space:
                norm_chars.append(" ")
                idx_map.append(i)
                prev_space = True

    if norm_chars and norm_chars[-1] == " ":
        norm_chars.pop()
        idx_map.pop()

    return "".join(norm_chars), idx_map

def tokens(norm: str) -> List[str]:
    return TOKEN_RE.findall(norm)

def build_phrase_index_from_csv(
    csv_path: str,
    column_name: str = "sanction_list",
    logger: logging.Logger | None = None,
):
    log = logger or logging.getLogger(__name__)
    t0 = time.time()

    seen_norm: Set[str] = set()
    phrases: List[Phrase] = []
    token_freq = Counter()

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or column_name not in reader.fieldnames:
            raise ValueError(f"CSV missing column '{column_name}'. Found columns: {reader.fieldnames}")

        row_count = 0
        raw_entity_count = 0
        for row in reader:
            row_count += 1
            cell = (row.get(column_name) or "").strip()
            if not cell:
                continue
            for item in cell.split(";"):
                raw_entity_count += 1
                raw = item.strip()
                if not raw:
                    continue
                norm, _ = normalize_with_map(raw)
                if not norm or norm in seen_norm:
                    continue
                seen_norm.add(norm)
                toks = tuple(tokens(norm))
                if not toks:
                    continue
                phrases.append(Phrase(raw=raw, norm=norm, toks=toks))
                token_freq.update(set(toks))

    anchor_index: Dict[str, List[int]] = defaultdict(list)
    for i, p in enumerate(phrases):
        anchor = min(set(p.toks), key=lambda t: token_freq.get(t, 10**9))
        anchor_index[anchor].append(i)

    log.info(
        "Sanctions loaded: rows=%d raw_entities=%d unique_entities=%d anchors=%d (%.2fs)",
        row_count, raw_entity_count, len(phrases), len(anchor_index), time.time() - t0
    )
    return phrases, dict(anchor_index), token_freq

def find_exact_matches(sentence: str, phrases, anchor_index, max_candidates: int = 50_000) -> List[Dict[str, Any]]:
    sent_norm, sent_map = normalize_with_map(sentence)
    if not sent_norm:
        return []
    sent_toks = set(tokens(sent_norm))
    if not sent_toks:
        return []

    cand_ids: Set[int] = set()
    for t in sent_toks:
        ids = anchor_index.get(t)
        if ids:
            cand_ids.update(ids)
            if len(cand_ids) >= max_candidates:
                break
    if not cand_ids:
        return []

    results: List[Dict[str, Any]] = []
    for pid in cand_ids:
        p = phrases[pid]
        start = 0
        while True:
            pos = sent_norm.find(p.norm, start)
            if pos == -1:
                break
            end = pos + len(p.norm)
            if end > len(sent_map):
                break
            orig_start = sent_map[pos]
            orig_end = sent_map[end - 1] + 1
            results.append({
                "entity": p.raw,
                "beginOffset": orig_start,
                "endOffset": orig_end,
                "matchedText": sentence[orig_start:orig_end],
            })
            start = pos + 1

    results.sort(key=lambda r: (r["beginOffset"], -(r["endOffset"] - r["beginOffset"])))
    return results
