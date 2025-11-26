# shapler_wrapper/cli.py

import argparse
import json
import uuid
from pathlib import Path

from .logger import get_logger
from .executor import run_gradle
from .parser import parse_multi_file_errors
from .snapshot import save_snapshot
from .diff_generator import generate_diff
from .config import SNAPSHOT_DIR

log = get_logger(__name__)


def dedupe(entries):
    seen = set()
    out = []
    for e in entries:
        key = (e["path"], e["line"])
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


# ---------------------------------------------------------
# RUN → BEFORE SNAPSHOTS ONLY
# ---------------------------------------------------------
def cmd_run(args):
    result = run_gradle(args.project, args.task)
    parsed = parse_multi_file_errors(result["full_log"], project_root=args.project)

    merged = dedupe(parsed["primary_errors"] + parsed["related_files"])

    if not merged:
        print({"status": "success", "message": "no errors detected"})
        return 0

    uid = uuid.uuid4().hex
    marker_file = SNAPSHOT_DIR / f"latest_error_{uid}.json"

    error_objects = []

    for err in merged:
        before = save_snapshot(err["path"], "before", err["line"])
        error_objects.append({
            "location": {
                "path": err["path"],
                "line": err["line"]
            },
            "details": {
                "type": err["error_type"],
                "message": err["error_message"],
                "error_code": err.get("error_code")
            },
            "before": before,
            "after": None,
            "diff": None
        })

    marker_file.write_text(json.dumps({
        "project": args.project,
        "task": args.task,
        "errors": error_objects
    }, indent=2))

    print({
        "status": "snapshot_created",
        "count": len(error_objects),
        "marker": str(marker_file)
    })
    return 0


# ---------------------------------------------------------
# FINALIZE → AFTER SNAPSHOTS + DIFF
# ---------------------------------------------------------
def cmd_finalize(args):
    markers = sorted(SNAPSHOT_DIR.glob("latest_error_*.json"))
    if not markers:
        print({"status": "error", "message": "no snapshot found"})
        return 1

    meta_file = markers[-1]
    meta = json.loads(meta_file.read_text())

    run_gradle(args.project, args.task)

    updated_errors = []

    for err in meta["errors"]:
        path = err["location"]["path"]
        line = err["location"]["line"]

        before = err["before"]
        after = save_snapshot(path, "after", line)

        diff = generate_diff(
            before_content=before["content"],
            after_content=after["content"],
            file_path=path
        )

        err["after"] = after
        err["diff"] = {"unified": diff}

        updated_errors.append(err)

    meta["errors"] = updated_errors

    meta_file.write_text(json.dumps(meta, indent=2))

    print({
        "status": "finalize_complete",
        "error_count": len(updated_errors),
        "marker": str(meta_file)
    })
    return 0


def main():
    parser = argparse.ArgumentParser(prog="shapler-build")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--project", "-p", required=True)
    p_run.add_argument("--task", "-t", required=True)
    p_run.set_defaults(func=cmd_run)

    p_finalize = sub.add_parser("finalize")
    p_finalize.add_argument("--project", "-p", required=True)
    p_finalize.add_argument("--task", "-t", required=True)
    p_finalize.set_defaults(func=cmd_finalize)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
