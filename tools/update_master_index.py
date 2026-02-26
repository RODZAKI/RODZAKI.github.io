import json
import subprocess
from datetime import datetime
from pathlib import Path
import re
import sys

MASTER_PATH = Path("canon") / "master-index.json"
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def is_staged(path: Path) -> bool:
    staged = run(["git", "diff", "--cached", "--name-only"])
    return str(path).replace("\\", "/") in staged.splitlines()

def bump_patch(version: str) -> str:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Version must be semver like 1.9.0 (got: {version})")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"

def main() -> int:
    if not MASTER_PATH.exists():
        print(f"[hook] Missing {MASTER_PATH}", file=sys.stderr)
        return 0

    if not is_staged(MASTER_PATH):
        return 0  # only act when master-index.json is part of this commit

    data = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})

    old_version = meta.get("version", "0.0.0")
    meta["version"] = bump_patch(old_version)
    meta["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")

    MASTER_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    subprocess.check_call(["git", "add", str(MASTER_PATH)])

    print(f"[hook] Master Index bumped {old_version} → {meta['version']} and updated lastUpdated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())