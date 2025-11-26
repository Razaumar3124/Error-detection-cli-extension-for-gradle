# shapler_wrapper/snapshot.py

from pathlib import Path
from typing import Dict, Any
from .utils import sha256_text, read_file_safe, git_blob_hash
from .logger import get_logger
import re

log = get_logger(__name__)

def strip_comments(content: str) -> str:
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return content

def extract_line(content: str, line_no: int) -> str:
    lines = content.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].rstrip()
    return ""

def save_snapshot(file_path: str, tag: str, error_line: int = None) -> Dict[str, Any]:
    src = Path(file_path)

    raw = read_file_safe(src)
    clean = strip_comments(raw)

    sha = sha256_text(clean)
    git_hash = git_blob_hash(src)

    if tag == "before":
        error_code = extract_line(raw, error_line) if error_line else None
        fixed_code = None
    else:
        error_code = None
        fixed_code = extract_line(raw, error_line) if error_line else None

    return {
        "path": str(src),
        "sha256_clean": sha,
        "git_hash": git_hash,
        "error_line": error_line if tag == "before" else None,
        "error_code": error_code,
        "fixed_code": fixed_code,
        "content": clean
    }
