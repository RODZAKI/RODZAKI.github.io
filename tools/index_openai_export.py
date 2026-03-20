import json
import csv
import os
from datetime import datetime, timezone

SHARDS_DIR = r"C:\Users\david\Downloads\Thunk-Threads 3-20-26"
SHARD_FILES = [f"conversations-{str(i).zfill(3)}.json" for i in range(6)]
OUTPUT_DIR = "artifacts/_staging"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "openai-thread-index.json")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "openai-thread-index.csv")

def ts(unix):
    if not unix:
        return ""
    return datetime.fromtimestamp(unix, tz=timezone.utc).isoformat()

def count_messages(mapping):
    return sum(
        1 for node in mapping.values()
        if node.get("message") and node["message"].get("author", {}).get("role") != "system"
    )

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    threads = []

    for shard in SHARD_FILES:
        path = os.path.join(SHARDS_DIR, shard)
        if not os.path.exists(path):
            print(f"Missing: {shard}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for convo in data:
            threads.append({
                "conversation_id": convo.get("conversation_id", ""),
                "title": convo.get("title", "Untitled"),
                "create_time": ts(convo.get("create_time")),
                "update_time": ts(convo.get("update_time")),
                "message_count": count_messages(convo.get("mapping", {})),
                "shard": shard
            })
        print(f"Processed {shard}: {len(data)} conversations")

    threads.sort(key=lambda x: x["create_time"])

    for i, thread in enumerate(threads):
        thread["index_order"] = i + 1

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"total": len(threads), "threads": threads}, f, indent=2)

    fields = ["index_order","conversation_id","title","create_time","update_time","message_count","shard"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(threads)

    print(f"\nDone. {len(threads)} threads indexed.")
    print(f"JSON → {OUTPUT_JSON}")
    print(f"CSV  → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()