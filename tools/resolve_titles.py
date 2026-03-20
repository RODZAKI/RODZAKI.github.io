import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "artifacts" / "_staging"
INPUT_JSON = STAGING / "openai-thread-index.json"
INPUT_CSV = STAGING / "openai-thread-index-marked.csv"
OUTPUT_CSV = STAGING / "openai-thread-index-resolved.csv"

SELECTED_COLUMN = "selected"
SELECTED_MARKER = "x"

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def normalize_row(row):
    out = dict(row)
    try:
        out["index_order"] = int(row["index_order"])
    except Exception:
        pass
    try:
        out["message_count"] = int(row["message_count"])
    except Exception:
        pass
    return out

def load_existing_resolved(path: Path):
    if not path.exists():
        return {}
    existing = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                idx = int(row["index_order"])
                existing[idx] = row
            except Exception:
                pass
    return existing

def main():
    json_data = load_json(INPUT_JSON)
    json_map = {}
    for row in json_data["threads"]:
        key = row.get("index_order")
        if key is not None:
            json_map[int(key)] = row

    csv_rows = [normalize_row(r) for r in load_csv_rows(INPUT_CSV)]

    selected = [
        r for r in csv_rows
        if str(r.get(SELECTED_COLUMN, "")).strip().lower() == SELECTED_MARKER
    ]

    if not selected:
        print("No rows marked with 'x' in the 'selected' column. Nothing written.")
        return

    existing = load_existing_resolved(OUTPUT_CSV)

    added = 0
    skipped = 0
    for row in selected:
        idx = row.get("index_order")
        if idx in existing:
            skipped += 1
            continue
        source = json_map.get(idx, {})
        full_title = (
            source.get("title")
            or source.get("conversation_title")
            or source.get("name")
            or row.get("title")
            or ""
        )
        existing[idx] = {
            "index_order": idx,
            "visible_title_csv": row.get("title", ""),
            "full_title": full_title,
            "message_count": row.get("message_count", ""),
            "bucket": row.get("bucket", ""),
        }
        added += 1

    resolved = sorted(
        existing.values(),
        key=lambda r: (-int(r["message_count"]), int(r["index_order"]))
    )

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index_order",
                "visible_title_csv",
                "full_title",
                "message_count",
                "bucket",
            ],
        )
        writer.writeheader()
        writer.writerows(resolved)

    print(f"Wrote: {OUTPUT_CSV}")
    print(f"Added: {added} new rows")
    print(f"Skipped: {skipped} duplicates")
    print(f"Total in resolved: {len(resolved)}")

if __name__ == "__main__":
    main()