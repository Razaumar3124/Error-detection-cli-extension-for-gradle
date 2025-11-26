# shapler_wrapper/diff_generator.py

import difflib

def generate_diff(before_content: str, after_content: str, file_path: str) -> str:
    before_lines = before_content.splitlines(keepends=True)
    after_lines = after_content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"{file_path} (before)",
        tofile=f"{file_path} (after)",
        n=3
    )

    return "".join(diff)
