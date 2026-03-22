import json
import os
from pathlib import Path
from datetime import datetime, timezone

SHARDS_DIR = r"C:\Users\david\Downloads\Thunk-Threads 3-20-26"
RESOLVED_CSV = r"C:\Users\david\Projects\RODZAKI.github.io\artifacts\_staging\openai-thread-index-resolved.csv"
OUTPUT_DIR = Path(r"C:\Users\david\Projects\RODZAKI.github.io\artifacts\threads")
INDEX_JSON = Path(r"C:\Users\david\Projects\RODZAKI.github.io\artifacts\_staging\openai-thread-index.json")

def load_index(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {t["conversation_id"]: t for t in data["threads"]}

def load_resolved(path):
    import csv
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows

def extract_text(mapping):
    nodes = {}
    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue
        role = msg.get("author", {}).get("role", "")
        if role not in ("user", "assistant"):
            continue
        parts = msg.get("content", {}).get("parts", [])
        text = " ".join(p for p in parts if isinstance(p, str)).strip()
        if text:
            nodes[node["id"]] = {"role": role, "text": text}

    root = None
    all_children = set()
    for node in mapping.values():
        for child in node.get("children", []):
            all_children.add(child)
    for nid in mapping:
        if nid not in all_children:
            root = nid
            break

    ordered = []
    visited = set()
    stack = [root] if root else list(mapping.keys())[:1]
    while stack:
        nid = stack.pop(0)
        if nid in visited:
            continue
        visited.add(nid)
        if nid in nodes:
            ordered.append(nodes[nid])
        children = mapping.get(nid, {}).get("children", [])
        stack = children + stack

    lines = []
    for node in ordered:
        prefix = "USER: " if node["role"] == "user" else "ASSISTANT: "
        lines.append(prefix + node["text"])

    return "\n\n".join(lines)

def main():
    index = load_index(INDEX_JSON)
    resolved = load_resolved(RESOLVED_CSV)

    id_to_meta = {}
    for entry in index.values():
        id_to_meta[entry["conversation_id"]] = entry

    conv_id_map = {}
    for t in index.values():
        conv_id_map[t["conversation_id"]] = t

    shard_cache = {}

    for row in resolved:
        idx = int(row["index_order"])
        full_title = row.get("full_title", "").strip()
        message_count = row.get("message_count", "0")

        meta = None
        for t in index.values():
            if t.get("index_order") == idx or int(t.get("index_order", -1)) == idx:
                meta = t
                break

        if not meta:
            print(f"No metadata for index_order {idx}, skipping.")
            continue

        shard = meta["shard"]
        conv_id = meta["conversation_id"]

        if shard not in shard_cache:
            shard_path = os.path.join(SHARDS_DIR, shard)
            with open(shard_path, "r", encoding="utf-8") as f:
                shard_cache[shard] = {c["conversation_id"]: c for c in json.load(f)}

        convo = shard_cache[shard].get(conv_id)
        if not convo:
            print(f"Conversation {conv_id} not found in {shard}, skipping.")
            continue

        text = extract_text(convo.get("mapping", {}))

        safe_id = f"openai-{idx:04d}"
        artifact = {
            "id": safe_id,
            "title": full_title,
            "source": f"/shards/{shard}#{conv_id}",
            "era": "openai",
            "text": text
        }

        out_path = OUTPUT_DIR / f"{safe_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        print(f"Extracted: {safe_id} — {full_title}")

    print("\nDone.")

if __name__ == "__main__":
    main()