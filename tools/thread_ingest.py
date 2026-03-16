import os
import json
from datetime import datetime

THREADS_DIR = "../threads"
CATALOG_PATH = "canon/thread-catalog.json"

def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_catalog(data):
    data["meta"]["lastUpdated"] = datetime.utcnow().isoformat()

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def next_legacy_id(existing_ids):
    numbers = []

    for id in existing_ids:
        if id.startswith("legacy-"):
            try:
                numbers.append(int(id.split("-")[1]))
            except:
                pass

    if not numbers:
        return "legacy-001"

    return f"legacy-{max(numbers)+1:03d}"

def main():
    catalog = load_catalog()

    known_files = set()
    existing_ids = set()

    for thread in catalog["threads"]:
        known_files.add(thread["pdf"])
        existing_ids.add(thread["id"])

    for file in os.listdir(THREADS_DIR):

        if not file.lower().endswith(".pdf"):
            continue

        path = f"/threads/{file}"

        if path in known_files:
            continue

        title = file.replace(".pdf", "")

        if title.startswith("Master Index"):
            id_value = title.replace("Master Index ", "")
            era = "indexed"
        else:
            id_value = next_legacy_id(existing_ids)
            era = "pre-index"

        entry = {
            "id": id_value,
            "title": title,
            "pdf": path,
            "era": era
        }

        catalog["threads"].append(entry)
        existing_ids.add(id_value)

        print(f"Added: {title}")

    save_catalog(catalog)
    print("Catalog updated.")

if __name__ == "__main__":
    main()