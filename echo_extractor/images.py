"""TIFF image loading, report-page detection, PHI cropping, and base64 encoding."""
from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from .grouping import ImageFile

log = logging.getLogger(__name__)

REPORT_SIZE = (1024, 768)   # width × height of report pages
PHI_FRACTION = 0.05         # top fraction to crop for PHI removal


def _image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size  # (width, height)


def filter_report_pages(image_files: list[ImageFile]) -> list[ImageFile]:
    """Return only the report pages (1024×768), warn if not exactly 4."""
    pages = [f for f in image_files if _image_size(f.path) == REPORT_SIZE]
    if len(pages) != 4:
        log.warning(
            "Patient %s: expected 4 report pages, found %d",
            image_files[0].patient_id if image_files else "?",
            len(pages),
        )
    return pages


def encode_page(path: Path, crop_phi: bool) -> tuple[str, str]:
    """Return (base64_data, media_type) for a report page as PNG.

    If crop_phi is True the top PHI_FRACTION of the image is removed before
    encoding so patient names are never sent to the API.
    """
    with Image.open(path) as img:
        if crop_phi:
            w, h = img.size
            top = int(h * PHI_FRACTION)
            img = img.crop((0, top, w, h))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = base64.standard_b64encode(buf.getvalue()).decode()
    return data, "image/png"
