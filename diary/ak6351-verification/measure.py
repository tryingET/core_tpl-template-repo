"""Retained AK6351 measurement harness; bounds belong to the recorded command."""
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

output = Path(sys.argv[1])
command = sys.argv[2:]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
start = time.monotonic_ns()
result = subprocess.run(command, check=False)
elapsed = time.monotonic_ns() - start
output.write_text(json.dumps({
    "command": command, "cwd": str(Path.cwd()), "started_utc": started,
    "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "elapsed_ns": elapsed, "elapsed_seconds": elapsed / 1_000_000_000,
    "exit_code": result.returncode,
}, indent=2) + "\n")
raise SystemExit(result.returncode)
