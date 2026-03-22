#!/usr/bin/env python3
"""
Deterministic artifact classification pass for Master Index 2.5.1

Version 1 goals:
- append classification metadata into each artifact JSON
- keep Dharma as universal membership with weight 1.0
- remain deterministic per version
- avoid mutating unrelated fields
- operate artifact-local, in place

Expected default repo layout:
- tools/classify.py
- artifacts/threads/*.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


DRAWER_ORDER = [
    "dharma",
    "logos",
    "maat",
    "dao",
    "rta",
    "ayni",
    "ubuntu",
    "mitakuye-oyasin",
    "sumak-kawsay",
]

ROW_ORDER = [
    "canonical",
    "developmental",
    "operational",
    
]

CLASSIFICATION_FIELD = "classification"


# -----------------------------
# Drawer lexicon
# -----------------------------
# Notes:
# - Dharma is universal membership and is injected at weight 1.0 later.
# - Other drawers are scored heuristically and normalized.
# - Phrases may carry higher weights than single tokens.
DRAWER_PATTERNS: Dict[str, Dict[str, float]] = {
    "logos": {
        r"\bprotocol\b": 2.2,
        r"\barchitecture\b": 2.2,
        r"\bschema\b": 2.0,
        r"\bstructure\b": 1.6,
        r"\bsystem\b": 1.8,
        r"\bsystems\b": 1.8,
        r"\bmodel\b": 1.6,
        r"\bmodels\b": 1.6,
        r"\bdesign\b": 1.4,
        r"\bdesign parameters\b": 2.1,
        r"\bformal\b": 1.4,
        r"\bformalized\b": 1.6,
        r"\bgovernance\b": 1.8,
        r"\bconstraint\b": 1.5,
        r"\bconstraints\b": 1.5,
        r"\binvariant\b": 1.8,
        r"\binvariants\b": 1.8,
        r"\bclassification\b": 1.8,
        r"\btransform\b": 1.7,
        r"\brenderer\b": 1.8,
        r"\bpipeline\b": 1.7,
    },
    "maat": {
        r"\bbalance\b": 1.8,
        r"\btruth\b": 1.8,
        r"\bintegrity\b": 2.2,
        r"\breconcile\b": 1.9,
        r"\breconciliation\b": 1.9,
        r"\baccountability\b": 2.2,
        r"\bmeasure\b": 1.7,
        r"\bmeasurement\b": 2.0,
        r"\baudit\b": 2.1,
        r"\bconsistency\b": 1.8,
        r"\bdeterministic\b": 2.4,
        r"\bversioning\b": 1.8,
        r"\bversion\b": 1.2,
        r"\bweighted\b": 1.5,
        r"\bconfidence\b": 1.8,
        r"\bdrift\b": 2.0,
        r"\bvalidation\b": 1.9,
        r"\barithmetic\b": 1.8,
        r"\brequirement\b": 1.5,
        r"\brequirements\b": 1.5,
    },
    "dao": {
        r"\bflow\b": 1.8,
        r"\bemergent\b": 2.0,
        r"\bemergence\b": 2.0,
        r"\badaptive\b": 1.8,
        r"\bevolution\b": 2.0,
        r"\bevolutionary\b": 2.2,
        r"\borganic\b": 1.9,
        r"\bnatural\b": 1.5,
        r"\bway\b": 1.2,
        r"\bprocess\b": 1.4,
        r"\bbecoming\b": 1.9,
        r"\bchange over time\b": 2.0,
        r"\bfield\b": 1.2,
        r"\brefine\b": 1.5,
    },
    "rta": {
        r"\border\b": 1.8,
        r"\bcosmic\b": 1.8,
        r"\blaw\b": 1.6,
        r"\blaws\b": 1.6,
        r"\bsequence\b": 1.7,
        r"\bcontinuity\b": 1.9,
        r"\blineage\b": 1.8,
        r"\bcanonical\b": 2.0,
        r"\bcanon\b": 2.0,
        r"\bsealed\b": 1.8,
        r"\bfossilized\b": 1.7,
        r"\bsuperseded\b": 1.7,
        r"\bnon-destructive\b": 2.0,
        r"\bthread closure\b": 1.7,
        r"\bcarry-forward\b": 1.7,
        r"\bmaster index\b": 1.8,
    },
    "ayni": {
        r"\breciprocal\b": 2.0,
        r"\breciprocity\b": 2.2,
        r"\bexchange\b": 1.4,
        r"\bmutual\b": 1.8,
        r"\bpartnership\b": 1.7,
        r"\bpartner\b": 1.5,
        r"\bcollaboration\b": 1.8,
        r"\bco-author\b": 1.8,
        r"\bco-creative\b": 1.9,
        r"\bsync\b": 1.3,
        r"\bhandoff\b": 1.5,
    },
    "ubuntu": {
        r"\bcommunity\b": 1.8,
        r"\bcollective\b": 1.8,
        r"\bshared\b": 1.5,
        r"\brelational\b": 1.7,
        r"\bnetwork\b": 1.5,
        r"\bhuman\b": 1.2,
        r"\bhumans\b": 1.2,
        r"\bwe\b": 0.3,
        r"\btogether\b": 1.5,
        r"\bbelonging\b": 1.8,
        r"\bcommons\b": 1.7,
    },
    "mitakuye-oyasin": {
        r"\ball my relations\b": 2.8,
        r"\bkinship\b": 2.2,
        r"\bancestral\b": 1.8,
        r"\bceremony\b": 1.8,
        r"\bsacred\b": 1.8,
        r"\bspirit\b": 1.6,
        r"\binterconnected\b": 1.9,
        r"\binterdependence\b": 1.9,
        r"\brelations\b": 1.4,
    },
    "sumak-kawsay": {
        r"\bwell-being\b": 2.2,
        r"\bflourishing\b": 2.0,
        r"\bliving well\b": 2.6,
        r"\bharmony\b": 1.8,
        r"\becology\b": 1.8,
        r"\becological\b": 1.8,
        r"\bregenerative\b": 2.0,
        r"\bsustainability\b": 1.9,
        r"\bresource-based\b": 1.8,
        r"\bpost-monetary\b": 2.1,
        r"\bquality of life\b": 2.2,
    },
}


ROW_PATTERNS: Dict[str, Dict[str, float]] = {
    "canonical": {
        r"\bcanonical\b": 3.0,
        r"\bcanon\b": 2.8,
        r"\bsealed\b": 2.5,
        r"\btreatise\b": 2.7,
        r"\bscroll\b": 2.0,
        r"\bfoundation\b": 2.2,
        r"\bgovernance constraint\b": 2.5,
        r"\binvariant\b": 2.2,
        r"\bprinciple\b": 1.8,
        r"\bmajor reflective piece\b": 2.4,
        r"\barchived\b": 1.6,
    },
    "developmental": {
        r"\bbuild\b": 1.7,
        r"\bbuilding\b": 1.9,
        r"\bdevelop\b": 2.0,
        r"\bdevelopment\b": 2.0,
        r"\brefine\b": 1.7,
        r"\biterate\b": 1.9,
        r"\broadmap\b": 1.7,
        r"\bnext move\b": 1.8,
        r"\bplanned\b": 1.5,
        r"\bscoped\b": 1.8,
        r"\bready\b": 1.2,
        r"\bprepared\b": 1.5,
        r"\bstructure\b": 1.2,
        r"\bversion 2\b": 1.9,
    },
    "operational": {
        r"\bscript\b": 2.2,
        r"\btools\/[a-z0-9_\-]+\.py\b": 3.0,
        r"\bclassify\.py\b": 3.0,
        r"\bexecute\b": 1.9,
        r"\brun\b": 1.1,
        r"\bcommands\b": 1.8,
        r"\bstep\b": 1.1,
        r"\bpipeline\b": 2.2,
        r"\btransform stage\b": 2.4,
        r"\bingestion\b": 1.8,
        r"\bjson\b": 1.4,
        r"\bwrite\b": 1.2,
        r"\bread\b": 1.1,
        r"\bfile\b": 1.1,
        r"\bthread closure\b": 1.5,
        r"\bartifact-local\b": 1.8,
    },
    "experimental": {
        r"\bprobe\b": 2.6,
        r"\bexperimental\b": 2.8,
        r"\btest\b": 1.5,
        r"\btesting\b": 1.8,
        r"\bhypothesis\b": 2.1,
        r"\bspeculative\b": 2.2,
        r"\bobserve system behavior\b": 2.5,
        r"\bpartner runs\b": 2.0,
        r"\bcompare\b": 1.3,
        r"\bdrift\b": 1.7,
    },
}


TITLE_BONUSES: Dict[str, Dict[str, float]] = {
    "master index": {"logos": 1.2, "maat": 1.2, "rta": 1.4},
    "thread closure": {"rta": 1.5, "maat": 0.8},
    "renderer": {"logos": 1.8},
    "schema": {"logos": 1.6},
    "pipeline": {"logos": 1.0, "operational": 1.4},
    "integration": {"developmental": 1.2, "logos": 0.8},
    "protocol": {"logos": 1.2, "canonical": 0.8},
    "treatise": {"canonical": 2.0, "rta": 0.8},
    "scroll": {"canonical": 1.6, "mitakuye-oyasin": 0.5},
    "experiment": {"experimental": 1.6},
    "probe": {"experimental": 1.8},
}


# -----------------------------
# JSON text extraction
# -----------------------------
def extract_strings(obj: Any, path: str = "") -> Iterable[Tuple[str, str]]:
    """
    Recursively yield (path, string_value) from JSON-like structures.

    We skip existing classification fields to avoid self-feedback loops.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == CLASSIFICATION_FIELD:
                continue
            next_path = f"{path}.{key}" if path else key
            yield from extract_strings(value, next_path)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            next_path = f"{path}[{idx}]"
            yield from extract_strings(value, next_path)
    elif isinstance(obj, str):
        text = obj.strip()
        if text:
            yield path, text


def artifact_text_and_title(data: Dict[str, Any], fallback_title: str) -> Tuple[str, str]:
    title_candidates = []
    for key in ("title", "name", "thread_title", "subject", "label"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            title_candidates.append(value.strip())

    title = title_candidates[0] if title_candidates else fallback_title

    parts: List[str] = []
    for path, value in extract_strings(data):
        # Favor likely content-bearing paths slightly by repeating once.
        low_path = path.lower()
        parts.append(value)
        if any(token in low_path for token in ("content", "body", "text", "messages", "cards", "segments")):
            parts.append(value)

    text = "\n".join(parts).strip()
    return text, title


# -----------------------------
# Scoring helpers
# -----------------------------
def safe_lower(text: str) -> str:
    return text.lower()


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def score_weighted_patterns(text: str, patterns: Dict[str, float]) -> float:
    score = 0.0
    for pattern, weight in patterns.items():
        hits = count_pattern(text, pattern)
        if hits:
            # Slight diminishing returns to avoid absurd overweighting from repetition
            score += weight * (1.0 + math.log1p(hits - 1))
    return score


def sentence_distribution_bonus(text: str, patterns: Dict[str, float]) -> float:
    """
    Reward distribution of signals across the text instead of a single clump.
    """
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    if not sentences:
        return 0.0

    matched_sentences = 0
    for sentence in sentences:
        if any(re.search(p, sentence, flags=re.IGNORECASE) for p in patterns):
            matched_sentences += 1

    if matched_sentences == 0:
        return 0.0

    ratio = matched_sentences / max(1, len(sentences))
    return min(1.5, ratio * 6.0)


def density_bonus(text: str, raw_score: float) -> float:
    words = re.findall(r"\b\w+\b", text)
    word_count = max(1, len(words))
    density = raw_score / math.sqrt(word_count)
    return min(1.5, density / 4.0)


def normalize_drawer_scores(raw_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize non-Dharma scores to a 0..1 range.
    Dharma is injected later as 1.0 universal membership.
    """
    non_dharma = {k: v for k, v in raw_scores.items() if k != "dharma"}
    max_score = max(non_dharma.values(), default=0.0)

    normalized: Dict[str, float] = {}
    for drawer in DRAWER_ORDER:
        if drawer == "dharma":
            continue
        score = raw_scores.get(drawer, 0.0)
        value = (score / max_score) if max_score > 0 else 0.0
        normalized[drawer] = round(min(1.0, max(0.0, value)), 4)

    normalized["dharma"] = 1.0
    return {drawer: normalized.get(drawer, 0.0) for drawer in DRAWER_ORDER}


def primary_drawer_from_weights(weights: Dict[str, float]) -> str:
    """
    Pick the strongest non-Dharma drawer if any signal exists.
    Otherwise default to Dharma.
    """
    candidates = [(drawer, weight) for drawer, weight in weights.items() if drawer != "dharma"]
    candidates.sort(key=lambda item: (-item[1], DRAWER_ORDER.index(item[0])))

    if not candidates or candidates[0][1] <= 0.0:
        return "dharma"
    return candidates[0][0]


def score_drawers(text: str, title: str) -> Dict[str, float]:
    text_l = safe_lower(text)
    title_l = safe_lower(title)

    scores: Dict[str, float] = {drawer: 0.0 for drawer in DRAWER_ORDER}

    for drawer, patterns in DRAWER_PATTERNS.items():
        raw = score_weighted_patterns(text_l, patterns)
        spread = sentence_distribution_bonus(text_l, patterns)
        density = density_bonus(text_l, raw)
        scores[drawer] += raw + spread + density

    for phrase, bonuses in TITLE_BONUSES.items():
        if phrase in title_l:
            for target, amount in bonuses.items():
                if target in scores:
                    scores[target] += amount

    return scores


def score_rows(text: str, title: str) -> Dict[str, float]:
    text_l = safe_lower(text)
    title_l = safe_lower(title)

    scores: Dict[str, float] = {row: 0.0 for row in ROW_ORDER}

    for row, patterns in ROW_PATTERNS.items():
        raw = score_weighted_patterns(text_l, patterns)
        spread = sentence_distribution_bonus(text_l, patterns)
        density = density_bonus(text_l, raw)
        scores[row] += raw + spread + density

    for phrase, bonuses in TITLE_BONUSES.items():
        if phrase in title_l:
            for target, amount in bonuses.items():
                if target in scores:
                    scores[target] += amount

    return scores


def choose_row_class(row_scores: Dict[str, float]) -> str:
    ranked = sorted(row_scores.items(), key=lambda item: (-item[1], ROW_ORDER.index(item[0])))
    top_name, top_score = ranked[0]

    # Low-signal fallback:
    if top_score <= 0.0:
        return "developmental"

    return top_name


def confidence_from_scores(drawer_scores: Dict[str, float], row_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    ranked_drawers = sorted(
        [(k, v) for k, v in weights.items() if k != "dharma"],
        key=lambda item: (-item[1], DRAWER_ORDER.index(item[0])),
    )
    ranked_rows = sorted(row_scores.items(), key=lambda item: (-item[1], ROW_ORDER.index(item[0])))

    top_drawer = ranked_drawers[0][1] if ranked_drawers else 0.0
    second_drawer = ranked_drawers[1][1] if len(ranked_drawers) > 1 else 0.0
    drawer_gap = max(0.0, top_drawer - second_drawer)

    top_row = ranked_rows[0][1] if ranked_rows else 0.0
    second_row = ranked_rows[1][1] if len(ranked_rows) > 1 else 0.0
    row_gap = max(0.0, top_row - second_row)

    raw_signal = sum(drawer_scores.values()) + sum(row_scores.values())

    if raw_signal <= 0.0:
        return 0.35

    confidence = 0.45
    confidence += min(0.25, top_drawer * 0.25)
    confidence += min(0.15, drawer_gap * 0.20)
    confidence += min(0.10, row_gap / 10.0)
    confidence += min(0.05, math.log1p(raw_signal) / 10.0)

    return round(min(0.98, max(0.35, confidence)), 4)


# -----------------------------
# Core classification
# -----------------------------
def classify_artifact(data: Dict[str, Any], artifact_id: str, version: str) -> Dict[str, Any]:
    text, title = artifact_text_and_title(data, fallback_title=artifact_id)

    drawer_scores = score_drawers(text, title)
    weights = normalize_drawer_scores(drawer_scores)
    primary_drawer = primary_drawer_from_weights(weights)

    row_scores = score_rows(text, title)
    row_class = choose_row_class(row_scores)

    confidence = confidence_from_scores(drawer_scores, row_scores, weights)

    return {
        "version": version,
        "primary_drawer": primary_drawer,
        "drawer_weights": weights,
        "row_class": row_class,
        "confidence": confidence,
    }


# -----------------------------
# File IO
# -----------------------------
def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def iter_artifact_files(artifacts_dir: Path) -> List[Path]:
    return sorted(
        [p for p in artifacts_dir.glob("*.json") if p.is_file()],
        key=lambda p: p.name.lower(),
    )


def process_file(path: Path, version: str, dry_run: bool = False) -> Dict[str, Any]:
    data = load_json(path)

    artifact_id = str(data.get("id") or path.stem)
    classification = classify_artifact(data, artifact_id=artifact_id, version=version)

    updated = dict(data)
    updated[CLASSIFICATION_FIELD] = classification

    if not dry_run:
        save_json(path, updated)

    return {
        "path": str(path),
        "id": artifact_id,
        "title": str(data.get("title") or path.stem),
        "primary_drawer": classification["primary_drawer"],
        "row_class": classification["row_class"],
        "confidence": classification["confidence"],
    }


# -----------------------------
# CLI
# -----------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify artifact JSON files and append artifact-local classification metadata."
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts/threads",
        help="Directory containing artifact JSON files. Default: artifacts/threads",
    )
    parser.add_argument(
        "--version",
        default="1.0",
        help='Classification version string. Default: "1.0"',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print summary without writing files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for testing. 0 means no limit.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        print(f"ERROR: artifacts directory not found: {artifacts_dir}", file=sys.stderr)
        return 1

    files = iter_artifact_files(artifacts_dir)
    if args.limit > 0:
        files = files[: args.limit]

    if not files:
        print(f"No JSON artifacts found in {artifacts_dir}")
        return 0

    results = []
    primary_counter: Counter[str] = Counter()
    row_counter: Counter[str] = Counter()

    for path in files:
        try:
            result = process_file(path, version=args.version, dry_run=args.dry_run)
            results.append(result)
            primary_counter[result["primary_drawer"]] += 1
            row_counter[result["row_class"]] += 1
            print(
                f"[OK] {result['id']}: "
                f"drawer={result['primary_drawer']} "
                f"row={result['row_class']} "
                f"confidence={result['confidence']}"
            )
        except Exception as exc:
            print(f"[ERROR] {path.name}: {exc}", file=sys.stderr)

    print("\n--- SUMMARY ---")
    print(f"Files processed: {len(results)}")
    print(f"Mode: {'dry-run' if args.dry_run else 'write'}")
    print(f"Version: {args.version}")

    print("\nPrimary drawers:")
    for drawer in DRAWER_ORDER:
        print(f"  {drawer}: {primary_counter.get(drawer, 0)}")

    print("\nRow classes:")
    for row in ROW_ORDER:
        print(f"  {row}: {row_counter.get(row, 0)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())