import json
import urllib.request
import urllib.error

SUPABASE_URL = "https://wteqinxdavkpvufsjjse.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0ZXFpbnhkYXZrcHZ1ZnNqanNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDgyMTQ3MSwiZXhwIjoyMDg2Mzk3NDcxfQ.KLXk3QbTFk5hOmf_wAXfQMSpiJpcRR3eqmVu4kIxHcc"
FIELD_ID = "7ac54512-7d16-4223-993b-bd848e1a8cf7"
CORPUS_PATH = "artifacts/thread-corpus.json"

def insert_artifact(artifact):
    url = SUPABASE_URL + "/rest/v1/artifacts"
    payload = json.dumps(artifact).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_KEY)
    req.add_header("Prefer", "return=minimal")
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("  ERROR " + str(e.code) + ": " + body)
        return False

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    threads = corpus.get("threads", [])
    print("Found " + str(len(threads)) + " threads. Seeding into field " + FIELD_ID)

    success = 0
    for thread in threads:
        artifact_url = "https://rodzaki.github.io/artifacts/threads/" + thread["id"] + ".json"
        try:
            with urllib.request.urlopen(artifact_url) as r:
                artifact_data = json.loads(r.read().decode())
        except Exception as e:
            print("  FETCH ERROR for " + thread["id"] + ": " + str(e))
            continue

        artifact = {
            "field_id": FIELD_ID,
            "type": "TREATISE",
            "state": "LIVE",
            "visibility": "FIELD_ONLY",
            "title": artifact_data.get("title", thread["id"]),
            "content": artifact_data.get("text", ""),
            "original_author": "David Killion",
        }

        print("  Inserting: " + artifact["title"])
        if insert_artifact(artifact):
            success += 1

    print("Done. " + str(success) + "/" + str(len(threads)) + " artifacts seeded.")

if __name__ == "__main__":
    main()