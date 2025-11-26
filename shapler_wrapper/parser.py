# shapler_wrapper/parser.py
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from .logger import get_logger

log = get_logger(__name__)


# ============================================================
#   REGEX DEFINITIONS FOR JAVAC, KOTLIN, SCALA
# ============================================================

JAVAC_ERROR_HEADER = re.compile(
    r"(?P<file>[^\s:]+?\.(java|kt|scala)):(?P<line>\d+):\s*(error|warning):\s*(?P<msg>.*)"
)

KOTLIN_ERROR = re.compile(
    r"e:\s*(?P<file>[^:]+):\s*\((?P<line>\d+),(?P<col>\d+)\):\s*(?P<msg>.+)"
)

STACKTRACE_REF = re.compile(
    r"at\s+[A-Za-z0-9_.]+\((?P<file>[^():]+\.(java|kt|scala)):(?P<line>\d+)\)"
)


# ============================================================
#   HELPER — EXTRACT FULL MULTI-LINE JAVAC BLOCK
# ============================================================

def extract_javac_block(log_text: str, file: str, line: int) -> str:
    """
    Extracts the full multi-line error message for Format B:

    App.java:8: error: cannot find symbol
        name = something
        ^
      symbol: variable name
      location: class App
    """

    lines = log_text.splitlines()
    collected = []
    capture = False

    pattern = f"{file}:{line}:"

    for l in lines:
        if pattern in l:
            capture = True

        if capture:
            collected.append(l.rstrip())

            # Javac blocks usually end when we hit a blank line OR a new file header
            if l.strip() == "" or JAVAC_ERROR_HEADER.match(l):
                break

    return "\n".join(collected).strip()


# ============================================================
#   HELPER — EXTRACT CODE LINE
# ============================================================

def extract_code_line(full_path: str, line: int) -> Optional[str]:
    try:
        p = Path(full_path)
        content = p.read_text(encoding="utf-8", errors="replace").splitlines()
        if 1 <= line <= len(content):
            return content[line - 1].strip()
    except:
        return None
    return None


# ============================================================
#   ERROR CLASSIFICATION (SMART)
# ============================================================

def classify_error(msg: str) -> str:
    lower = msg.lower()

    if "cannot find symbol" in lower:
        return "symbol_not_found"
    if "';' expected" in lower:
        return "missing_semicolon"
    if "unclosed string literal" in lower:
        return "unclosed_string"
    if "incompatible types" in lower:
        return "type_mismatch"
    if "not a statement" in lower:
        return "invalid_statement"
    if "missing return statement" in lower:
        return "missing_return"
    if "variable might not have been initialized" in lower:
        return "uninitialized_variable"
    if "error" in lower:
        return "compile_error"
    if "exception" in lower:
        return "runtime_exception"

    return "unknown"


# ============================================================
#   PATH VALIDATION
# ============================================================

def is_project_source_file(full_path: Path, project_root: str) -> bool:
    try:
        src = Path(project_root) / "app" / "src"
        resolved = full_path.resolve()
        return resolved.exists() and str(resolved).startswith(str(src.resolve()))
    except:
        return False


def resolve_path(raw: str, project_root: str) -> Optional[str]:
    candidate = Path(project_root) / raw
    if is_project_source_file(candidate, project_root):
        return str(candidate.resolve())
    return None


# ============================================================
#   MAIN: MULTI-FILE ERROR PARSER
# ============================================================

def parse_multi_file_errors(log_text: str, project_root: Optional[str]) -> Dict[str, Any]:
    primary = []

    # -------------------------------
    # 1. Match JAVAC Format B Errors
    # -------------------------------
    for m in JAVAC_ERROR_HEADER.finditer(log_text):
        raw = m.group("file")
        line = int(m.group("line"))
        msg = m.group("msg").strip()

        full_path = resolve_path(raw, project_root)
        if not full_path:
            continue

        # Capture full multi-line message
        full_msg = extract_javac_block(log_text, raw, line)

        # Classify type
        error_type = classify_error(full_msg)

        # Extract error-causing source code line
        code_line = extract_code_line(full_path, line)

        primary.append({
            "path": full_path,
            "line": line,
            "error_type": error_type,
            "error_message": full_msg,
            "error_code": code_line
        })

    # -------------------------------
    # 2. Kotlin "e:" Format
    # -------------------------------
    for m in KOTLIN_ERROR.finditer(log_text):
        raw = m.group("file")
        line = int(m.group("line"))
        msg = m.group("msg").strip()

        full_path = resolve_path(raw, project_root)
        if not full_path:
            continue

        error_type = classify_error(msg)
        code_line = extract_code_line(full_path, line)

        primary.append({
            "path": full_path,
            "line": line,
            "error_type": error_type,
            "error_message": msg,
            "error_code": code_line
        })

    # -------------------------------
    # 3. Stacktrace references (non-primary)
    # -------------------------------
    related = []
    for m in STACKTRACE_REF.finditer(log_text):
        raw = m.group("file")
        line = int(m.group("line"))

        full_path = resolve_path(raw, project_root)
        if not full_path:
            continue

        related.append({
            "path": full_path,
            "line": line,
            "error_type": "stacktrace_reference",
            "error_message": "Referenced in stacktrace",
            "error_code": extract_code_line(full_path, line)
        })

    return {
        "primary_errors": primary,
        "related_files": related
    }
