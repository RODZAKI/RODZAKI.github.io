import json
import urllib.request
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://wteqinxdavkpvufsjjse.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0ZXFpbnhkYXZrcHZ1ZnNqanNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4MjE0NzEsImV4cCI6MjA4NjM5NzQ3MX0.mREQi5l3U1SBv3rtayTu3oZCORBgJrTfTBY5Lu02sAQ"
FIELD_ID = "7ac54512-7d16-4223-993b-bd848e1a8cf7"

HEADERS = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def fmt(a):
    return f"  [{float(a.get('confidence') or 0):.4f}] {a.get('title', '')} — {a.get('primary_drawer', '')} / {a.get('row_class', '')}"

def main():
    print("Fetching all artifacts...\n")
    artifacts = supabase_get(
        f"artifacts?field_id=eq.{FIELD_ID}&select=id,title,primary_drawer,row_class,confidence,alignment_flag,era,resolving,window_scores_blob"
    )
    print(f"Total artifacts: {len(artifacts)}\n")
    print("=" * 60)

    total = len(artifacts)

    # --- ROW CLASS DISTRIBUTION ---
    row_class_counts = defaultdict(int)
    for a in artifacts:
        rc = a.get("row_class") or "unclassified"
        row_class_counts[rc] += 1

    print("\n⟁ ROW CLASS DISTRIBUTION\n")
    for rc, count in sorted(row_class_counts.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100, 1)
        print(f"  {rc:<20} {count:>3}  ({pct}%)")

    # --- PRIMARY DRAWER DISTRIBUTION ---
    drawer_counts = defaultdict(int)
    for a in artifacts:
        pd = a.get("primary_drawer") or "unclassified"
        drawer_counts[pd] += 1

    print("\n⟁ PRIMARY DRAWER DISTRIBUTION\n")
    for drawer, count in sorted(drawer_counts.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100, 1)
        print(f"  {drawer:<25} {count:>3}  ({pct}%)")

    # --- CONFIDENCE STATS ---
    confidences = [float(a.get("confidence") or 0.0) for a in artifacts]
    avg_conf = round(sum(confidences) / len(confidences), 4)
    min_conf = round(min(confidences), 4)
    max_conf = round(max(confidences), 4)

    print("\n⟁ CONFIDENCE STATS\n")
    print(f"  avg: {avg_conf}  min: {min_conf}  max: {max_conf}")

    # --- LOW CONFIDENCE ARTIFACTS ---
    low_conf = sorted(
        [a for a in artifacts if float(a.get("confidence") or 0.0) < 0.05],
        key=lambda x: float(x.get("confidence") or 0.0)
    )
    print(f"\n⟁ LOW CONFIDENCE ARTIFACTS (< 0.05)  [{len(low_conf)} total]\n")
    for a in low_conf:
        print(fmt(a))

    # --- HIGH CONFIDENCE ARTIFACTS ---
    high_conf = sorted(
        [a for a in artifacts if float(a.get("confidence") or 0.0) >= 0.4],
        key=lambda x: -float(x.get("confidence") or 0.0)
    )
    print(f"\n⟁ HIGH CONFIDENCE ARTIFACTS (>= 0.4)  [{len(high_conf)} total]\n")
    for a in high_conf:
        print(fmt(a))

    # --- FLAGGED ARTIFACTS ---
    flagged = [a for a in artifacts if a.get("alignment_flag")]
    print(f"\n⟁ ALIGNMENT FLAGGED ARTIFACTS  [{len(flagged)} total]\n")
    for a in flagged:
        print(f"  {a.get('title', '')} — {a.get('primary_drawer', '')} / {a.get('row_class', '')}")

    # --- ERA BREAKDOWN ---
    era_counts = defaultdict(int)
    for a in artifacts:
        era = a.get("era") or "unknown"
        era_counts[era] += 1

    print("\n⟁ ERA BREAKDOWN\n")
    for era, count in sorted(era_counts.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100, 1)
        print(f"  {era:<20} {count:>3}  ({pct}%)")

    # --- DIFFUSE ARTIFACTS ---
    diffuse = [a for a in artifacts if a.get("row_class") == "diffuse"]
    print(f"\n⟁ DIFFUSE ARTIFACTS  [{len(diffuse)} total]\n")
    for a in diffuse:
        blob = a.get("window_scores_blob") or {}
        wc = blob.get("window_count", "?")
        print(f"  {a.get('title', '')} — windows: {wc} | confidence: {float(a.get('confidence') or 0):.4f}")

    # --- RESOLVING ARTIFACTS ---
    resolving = [a for a in artifacts if a.get("resolving")]
    print(f"\n⟁ RESOLVING ARTIFACTS  [{len(resolving)} total]\n")
    for a in resolving:
        print(f"  {a.get('title', '')}")

    print("\n" + "=" * 60)
    print("Analysis complete. No changes made.\n")

if __name__ == "__main__":
    main()