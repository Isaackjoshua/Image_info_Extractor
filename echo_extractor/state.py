"""Persistent state: track which patients have been processed."""
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


class ProcessingState:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._processed: set[str] = set()
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with open(self._path) as f:
                data = json.load(f)
            self._processed = set(data.get("processed", []))
            log.debug("Loaded state: %d processed patient(s)", len(self._processed))

    def is_processed(self, patient_id: str) -> bool:
        return patient_id in self._processed

    def mark_processed(self, patient_id: str) -> None:
        self._processed.add(patient_id)
        self._save()

    def _save(self) -> None:
        parent = self._path.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=parent, suffix=".json.tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump({"processed": sorted(self._processed)}, f, indent=2)
                os.fsync(f.fileno())
            os.rename(tmp_path, self._path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
