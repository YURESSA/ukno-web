import subprocess
import sys
from pathlib import Path


def test_error_message_catalog_matches_backend_sources():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "backend/core/scripts/generate_error_docs.py", "--check"],
        cwd=root, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
