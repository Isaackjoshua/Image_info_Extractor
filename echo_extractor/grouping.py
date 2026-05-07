"""Parse TIFF filenames and group images by patient."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class ImageFile:
    path: Path
    patient_id: str
    exam_id: Optional[str]
    image_num: int


def parse_filename(filepath: Path) -> Optional[ImageFile]:
    """Parse a TIFF filename into structured metadata.

    Handles two formats:
      1. {patient_id}_{DD.MM.YYYY.HH.MM.SS}_{num}.tif   (actual)
      2. {exam_id}_{patient_id}_{DD}_{MM}_{YYYY}_{HH}_{MM}_{SS}_{num}.tif (spec)
    """
    if filepath.suffix.lower() not in (".tif", ".tiff"):
        return None

    name = filepath.stem
    parts = name.split("_")

    if len(parts) < 2:
        log.debug("Cannot parse filename (too few segments): %s", filepath.name)
        return None

    # Format 1: second segment contains dots → date.time block
    if len(parts) >= 3 and "." in parts[1]:
        patient_id = parts[0]
        try:
            image_num = int(parts[-1])
        except ValueError:
            log.debug("Cannot parse image number from: %s", filepath.name)
            return None
        return ImageFile(path=filepath, patient_id=patient_id, exam_id=None, image_num=image_num)

    # Format 2: first segment is all digits → exam_id
    if len(parts) >= 9 and parts[0].isdigit():
        exam_id = parts[0]
        patient_id = parts[1]
        try:
            image_num = int(parts[-1])
        except ValueError:
            log.debug("Cannot parse image number from: %s", filepath.name)
            return None
        return ImageFile(path=filepath, patient_id=patient_id, exam_id=exam_id, image_num=image_num)

    log.debug("Unrecognised filename format: %s", filepath.name)
    return None


def group_by_patient(images_dir: Path) -> dict[str, list[ImageFile]]:
    """Return a mapping of patient_id → sorted list of ImageFile objects."""
    groups: dict[str, list[ImageFile]] = {}

    for f in images_dir.iterdir():
        if f.suffix.lower() not in (".tif", ".tiff"):
            continue
        img = parse_filename(f)
        if img is None:
            continue
        groups.setdefault(img.patient_id, []).append(img)

    for patient_id in groups:
        groups[patient_id].sort(key=lambda x: x.image_num)

    log.info("Found %d patient(s) in %s", len(groups), images_dir)
    return groups
