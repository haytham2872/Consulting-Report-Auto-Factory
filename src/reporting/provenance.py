"""Provenance helpers to embed reproducibility metadata into artifacts."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _git_commit_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_summary_with_provenance(path: Path, model_name: str | None = None, token_usage: Dict[str, int] | None = None) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    metadata = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": file_sha256(path),
        "git_commit": _git_commit_hash(),
    }
    if model_name:
        metadata["model"] = model_name
    if token_usage:
        metadata["token_usage"] = token_usage

    data.setdefault("metadata", {}).update(metadata)
    return data
