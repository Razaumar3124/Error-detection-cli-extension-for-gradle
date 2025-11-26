# shapler_wrapper/utils.py
import hashlib
from pathlib import Path
import platform
import subprocess
import os

def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def read_file_safe(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return f.read()

def select_gradle_cmd(project_path: Path):
    """
    Returns system-appropriate gradle wrapper command.
    """
    system = platform.system().lower()
    if "win" in system:
        wrapper = project_path / "gradlew.bat"
    else:
        wrapper = project_path / "gradlew"

    if wrapper.exists():
        return [str(wrapper)]
    return ["gradle"]

def git_blob_hash(path: Path) -> str:
    """
    Computes git blob hash for the file content.
    Falls back to SHA256 if .git repo not found.
    """
    try:
        # Ensure we're inside a git repo
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(path.parent),
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Compute blob hash
        out = subprocess.check_output(
            ["git", "hash-object", str(path)],
            cwd=repo_root,
            stderr=subprocess.DEVNULL
        )
        return out.decode().strip()

    except Exception:
        # fallback if not inside a git repo
        content = read_file_safe(path)
        return sha256_text(content)
