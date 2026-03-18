import json
import os
import pymupdf

# Paths relative to repo root
CATALOG_PATH = "apex/canon/thread-catalog.json"
THREADS_DIR = "threads"
OUTPUT_DIR = "artifacts/threads"

def main():
    # Load thread catalog
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    threads = catalog.get("threads", [])
    print(f"Found {len(threads)} threads in catalog.")

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for thread in threads:
        thread_id = thread.get("id")
        title = thread.get("title")
        pdf_path_raw = thread.get("pdf", "")
        era = thread.get("era", "")

        # pdf field is like "/threads/Master Index 1.6.1.pdf"
        # Strip the leading slash and use as relative path
        pdf_relative = pdf_path_raw.lstrip("/")
        pdf_full_path = pdf_relative  # e.g. "threads/Master Index 1.6.1.pdf"

        if not os.path.exists(pdf_full_path):
            print(f"  MISSING: {pdf_full_path} — skipping.")
            continue

        print(f"  Extracting: {pdf_full_path}")

        try:
            doc = pymupdf.open(pdf_full_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            full_text = "\n".join(text_parts)
            doc.close()
        except Exception as e:
            print(f"  ERROR reading {pdf_full_path}: {e}")
            continue

        artifact = {
            "id": thread_id,
            "title": title,
            "pdf": pdf_path_raw,
            "era": era,
            "text": full_text
        }

        output_filename = f"{thread_id}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(artifact, out, ensure_ascii=False, indent=2)

        print(f"  Wrote: {output_path}")

    print("Done.")

if __name__ == "__main__":
    main()