import json
import os

ARTIFACTS_DIR = "artifacts/threads"
OUTPUT_PATH = "artifacts/thread-corpus.json"

def main():
    entries = []
    for filename in sorted(os.listdir(ARTIFACTS_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(ARTIFACTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        entries.append({
            "id": data.get("id"),
            "title": data.get("title"),
            "pdf": data.get("pdf"),
            "era": data.get("era"),
            "file": "artifacts/threads/" + filename
        })
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump({"threads": entries}, out, ensure_ascii=False, indent=2)
    print("Wrote " + str(len(entries)) + " entries to " + OUTPUT_PATH)

if __name__ == "__main__":
    main()