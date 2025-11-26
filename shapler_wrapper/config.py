# shapler_wrapper/config.py
from pathlib import Path

ROOT = Path.cwd()
TMP = ROOT / "tmp"
SNAPSHOT_DIR = TMP / "snapshots"
DIFF_DIR = TMP / "diffs"
LOG_DIR = ROOT / "logs"

# Ensure dirs exist
for p in (SNAPSHOT_DIR, DIFF_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)
