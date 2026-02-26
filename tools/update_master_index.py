import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime


MASTER_PATH = Path("canon/master-index.json")


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3:
        return "0.0.1"
    major, minor, patch = parts
    try:
        patch = str(int(patch) + 1)
    except ValueError:
        patch = "1"
    return f"{major}.{minor}.{patch}"


def main() -> int:
    if not MASTER_PATH.exists():
        print("[hook] master-index.json not found.")
        return 0

    data = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})

    # --- Version bump ---
    old_version = meta.get("version", "0.0.0")
    meta["version"] = bump_patch(old_version)

    # --- Update date ---
    meta["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")

    # --- Remove existing hash before recomputing ---
    meta.pop("hash", None)

    # --- First serialization (without hash) ---
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    # --- Compute SHA256 ---
    sha = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    # --- Inject hash ---
    meta["hash"] = sha

    # --- Final serialization (with hash) ---
    final_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    MASTER_PATH.write_text(final_text, encoding="utf-8")

    # --- Stage file ---
    subprocess.check_call(["git", "add", str(MASTER_PATH)])

    print(f"[hook] Master Index bumped {old_version} -> {meta['version']} and hash updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())