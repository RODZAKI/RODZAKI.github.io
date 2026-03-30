import json
import urllib.request
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://wteqinxdavkpvufsjjse.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0ZXFpbnhkYXZrcHZ1ZnNqanNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDgyMTQ3MSwiZXhwIjoyMDg2Mzk3NDcxfQ.KLXk3QbTFk5hOmf_wAXfQMSpiJpcRR3eqmVu4kIxHcc"
FIELD_ID = "7ac54512-7d16-4223-993b-bd848e1a8cf7"
WINDOW_SIZE = 2500
OVERLAP_RATIO = 0.3
DIFFUSE_CONFIDENCE_THRESHOLD = 0.05
DIFFUSE_WINDOW_THRESHOLD = 500

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

NARRATIVE_PATTERNS = [
    r"\bACT\s?\d",
    r"\bScene\b",
    r"\bsaid\b",
    r"\bhe said\b",
    r"\bshe said\b",
    r"\bthey said\b",
    r"\bwalked\b",
    r"\blooked\b",
    r"\bturned\b",
    r"\bbegan\b",
    r"\bchapter\b",
]

CANONICAL_PATTERNS = [
    r"\bis not a\b",
    r"\bis a\b",
    r"\brepresents\b",
    r"\bserves as\b",
    r"\bthis is\b",
    r"\bthis means\b",
    r"\bfundamentally\b",
    r"\bat its core\b",
    r"\bthe structure of\b",
    r"\bwe can see\b",
    r"\bby definition\b",
    r"\binvariant\b",
    r"\baxiom\b",
    r"\bground truth\b",
    r"\bimmutable\b",
    r"\birreducible\b",
]

OPERATIONAL_PATTERNS = [
    r"\bnext step\b",
    r"\bdo this\b",
    r"\brun this\b",
    r"\bimplement\b",
    r"\bapply\b",
    r"\bexecute\b",
    r"\bwe now\b",
    r"\bfrom here\b",
    r"\bthe system does\b",
    r"\bdeploy\b",
    r"\bbuild\b",
    r"\bpipeline\b",
    r"\bprocedure\b",
    r"\bsettings\b",
    r"\bpractical\b",
]

DRAWER_KEYWORDS = {
    "dharma": [
        "foundational", "primitive", "axiom", "invariant", "canonical", "ontology",
        "definition", "ground truth", "origin", "constitutional", "irreducible",
        "domain-8", "epistemic", "constraint", "non-negotiable", "layer", "mold",
        "casting", "framework", "architecture", "topology", "substrate"
    ],
    "logos": [
        "index", "map", "mapping", "catalog", "registry", "lookup", "taxonomy",
        "transfer", "orientation", "primer", "pointer", "reference", "classify",
        "synthetic", "construct", "handoff", "node", "activation", "seed"
    ],
    "maat": [
        "rule", "protocol", "governance", "constraint", "enforcement", "policy",
        "stewardship", "accountability", "reversibility", "kill-switch", "limits",
        "compliance", "canon", "law", "must not", "forbidden", "guardrail", "rls",
        "rights", "permission", "contract"
    ],
    "dao": [
        "publication", "output", "finished", "deliverable", "release", "draft",
        "vector", "direction", "flow", "motion", "animation", "design", "visual",
        "style", "creative", "directive", "aesthetic", "render", "produce"
    ],
    "rta": [
        "build", "construction", "architecture", "system", "engine", "core",
        "magnum opus", "cycle", "iteration", "work in progress", "active",
        "development", "mechanism", "pipeline", "scaffold", "infrastructure"
    ],
    "ayni": [
        "cycle", "serial", "sequence", "iteration", "version", "recurring",
        "exchange", "reciprocal", "chain", "continuation", "series", "episode",
        "follow-up", "previous", "next", "3.0", "2.0", "1.0"
    ],
    "ubuntu": [
        "essay", "reflection", "human", "collective", "emergence", "consciousness",
        "society", "civilization", "relationship", "community", "together",
        "wisdom", "philosophy", "perspective", "reasoning", "narrative", "story"
    ],
    "mitakuye-oyasin": [
        "note", "observation", "fragment", "sketch", "loose", "exploratory",
        "motion design", "animation", "principles", "practical", "tip", "guide",
        "how to", "settings", "parameters", "technique", "tool"
    ],
    "sumak-kawsay": [
        "unresolved", "ongoing", "open", "becoming", "evolving", "draft",
        "incomplete", "in progress", "still forming", "not yet", "continuance"
    ]
}

ROW_CLASS_KEYWORDS = {
    "canonical": ["canonical", "foundational", "primitive", "invariant", "axiom", "law", "ground truth", "immutable", "irreducible", "ontology"],
    "operational": ["build", "deploy", "run", "execute", "pipeline", "tool", "settings", "practical", "implementation", "procedure"],
    "developmental": ["cycle", "iteration", "version", "in progress", "draft", "evolving", "vector", "emerging", "forming", "candidate"],
    "transitional": ["transition", "shift", "becoming", "between", "resolving", "evolving into", "emergence", "in-between", "bridging"]
}

def detect_narrative(text):
    for pattern in NARRATIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def count_patterns(text, patterns):
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))

def make_windows(text):
    step = int(WINDOW_SIZE * (1 - OVERLAP_RATIO))
    windows = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + WINDOW_SIZE, len(text))
        windows.append({"index": idx, "start": start, "end": end, "text": text[start:end]})
        if end == len(text):
            break
        start += step
        idx += 1
    return windows

def score_window(text):
    text_lower = text.lower()
    word_count = max(len(text_lower.split()), 1)
    scores = {}
    for drawer, keywords in DRAWER_KEYWORDS.items():
        hits = sum(text_lower.count(kw.lower()) for kw in keywords)
        normalized = hits / (word_count / 100)
        scores[drawer] = round(min(normalized, 1.0), 4)
    return scores

def score_row_class(text, window_count, confidence):
    # Diffuse detection — must come first
    if confidence < DIFFUSE_CONFIDENCE_THRESHOLD and window_count > DIFFUSE_WINDOW_THRESHOLD:
        return "diffuse"

    # Narrative override
    if detect_narrative(text):
        return "developmental"

    # Pattern-based scoring
    canonical_score = count_patterns(text, CANONICAL_PATTERNS)
    operational_score = count_patterns(text, OPERATIONAL_PATTERNS)

    # Keyword-based scoring
    text_lower = text.lower()
    kw_scores = {rc: sum(text_lower.count(kw.lower()) for kw in kws)
                 for rc, kws in ROW_CLASS_KEYWORDS.items()}

    # Combine pattern and keyword scores
    combined = {
        "canonical": canonical_score * 2 + kw_scores["canonical"],
        "operational": operational_score * 2 + kw_scores["operational"],
        "developmental": kw_scores["developmental"],
        "transitional": kw_scores["transitional"],
    }

    top_class = max(combined, key=combined.get)
    top_score = combined[top_class]

    MIN_SIGNAL = 2
    if top_score < MIN_SIGNAL:
        return "developmental"

    if top_class == "transitional":
        other_scores = {k: v for k, v in combined.items() if k != "transitional"}
        if max(other_scores.values()) < MIN_SIGNAL:
            return "developmental"

    return top_class

def aggregate_windows(window_scores_list):
    totals = {d: 0.0 for d in DRAWER_KEYWORDS}
    for ws in window_scores_list:
        for d, v in ws.items():
            totals[d] += v
    n = len(window_scores_list)
    return {d: round(totals[d] / n, 4) for d in totals}

def compute_peaks(window_scores_list):
    peaks = {d: 0.0 for d in DRAWER_KEYWORDS}
    for ws in window_scores_list:
        for d, v in ws.items():
            if v > peaks[d]:
                peaks[d] = v
    return peaks

def compute_primary(weights):
    return max(weights, key=weights.get)

def compute_confidence(weights):
    sorted_vals = sorted(weights.values(), reverse=True)
    if len(sorted_vals) < 2:
        return sorted_vals[0] if sorted_vals else 0
    return round(sorted_vals[0] - sorted_vals[1], 4)

def check_alignment_flag(primary_drawer, row_class):
    if row_class == "diffuse":
        return False
    bias = {
        "canonical": "Shiva",
        "developmental": "Spanda",
        "operational": "Shakti",
        "transitional": "Spanda"
    }
    drawer_row = {
        "dharma": "Shiva", "logos": "Shiva", "maat": "Shiva",
        "dao": "Spanda", "rta": "Spanda", "ayni": "Spanda",
        "ubuntu": "Shakti", "mitakuye-oyasin": "Shakti", "sumak-kawsay": "Shakti"
    }
    return drawer_row.get(primary_drawer) != bias.get(row_class)

def supabase_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def supabase_patch(artifact_id, data):
    url = f"{SUPABASE_URL}/rest/v1/artifacts?id=eq.{artifact_id}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def main():
    print("Fetching unclassified artifacts...")
    artifacts = supabase_get(
        f"artifacts?field_id=eq.{FIELD_ID}&primary_drawer=is.null&select=id,title,content"
    )
    print(f"Found {len(artifacts)} unclassified artifacts.\n")

    for a in artifacts:
        title = a.get("title", "")
        content = a.get("content", "") or ""
        text = f"{title} {content}"

        windows = make_windows(text)
        window_count = len(windows)
        window_scores = []
        window_records = []

        for w in windows:
            scores = score_window(w["text"])
            window_scores.append(scores)
            window_records.append({
                "index": w["index"],
                "start": w["start"],
                "end": w["end"],
                "drawer_scores": scores
            })

        weights = aggregate_windows(window_scores)
        peaks = compute_peaks(window_scores)
        primary = compute_primary(weights)
        confidence = compute_confidence(weights)
        row_class = score_row_class(text, window_count, confidence)
        alignment_flag = check_alignment_flag(primary, row_class)

        window_blob = {
            "window_size": WINDOW_SIZE,
            "overlap_ratio": OVERLAP_RATIO,
            "window_count": window_count,
            "windows": window_records,
            "window_peaks": peaks
        }

        print(f"{title}")
        print(f"  windows: {window_count} | primary: {primary} | confidence: {confidence} | row_class: {row_class} | flag: {alignment_flag}")

        update = {
            "primary_drawer": primary,
            "drawer_weights": weights,
            "row_class": row_class,
            "confidence": confidence,
            "alignment_flag": alignment_flag,
            "resolving": False,
            "window_scores_blob": window_blob
        }

        supabase_patch(a["id"], update)
        print(f"  Saved.\n")

    print("Done. All unclassified artifacts processed.")

if __name__ == "__main__":
    main()