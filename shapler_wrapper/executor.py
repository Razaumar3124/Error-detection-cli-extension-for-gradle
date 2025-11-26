# shapler_wrapper/executor.py
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from .logger import get_logger
from .utils import select_gradle_cmd
from .config import LOG_DIR

log = get_logger(__name__)

def run_gradle(project_path: str, task: str, timeout: int = 300) -> Dict[str, Any]:
    project = Path(project_path)
    if not project.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")

    cmd = select_gradle_cmd(project)
    cmd += [task, "--no-daemon", "--stacktrace"]

    log.debug("Running: %s in %s", " ".join(cmd), project_path)

    proc = subprocess.Popen(
        cmd,
        cwd=str(project_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate(timeout=timeout)
    full_log = stdout + "\n" + stderr

    # Save log to logs folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"build_{timestamp}.log"
    log_file.write_text(full_log, encoding="utf-8")
    log.info("Saved build log -> %s", log_file)

    return {
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "full_log": full_log,
        "log_file": str(log_file)
    }
