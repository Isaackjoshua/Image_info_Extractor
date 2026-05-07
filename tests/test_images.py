"""Tests for report-page detection."""
import io
import pytest
from pathlib import Path
from PIL import Image

from echo_extractor.images import REPORT_SIZE, filter_report_pages
from echo_extractor.grouping import ImageFile


def _make_tif(path: Path, size: tuple[int, int]) -> Path:
    img = Image.new("RGB", size, color=(0, 0, 0))
    img.save(path, format="TIFF")
    return path


def _img_file(path: Path, num: int) -> ImageFile:
    return ImageFile(path=path, patient_id="TEST", exam_id=None, image_num=num)


class TestFilterReportPages:
    def test_identifies_report_pages(self, tmp_path):
        report = _make_tif(tmp_path / "r.tif", REPORT_SIZE)
        scan = _make_tif(tmp_path / "s.tif", (1152, 864))
        pages = filter_report_pages([_img_file(report, 1), _img_file(scan, 2)])
        assert len(pages) == 1
        assert pages[0].path == report

    def test_warns_if_not_four_pages(self, tmp_path, caplog):
        import logging
        reports = [_make_tif(tmp_path / f"r{i}.tif", REPORT_SIZE) for i in range(2)]
        imgs = [_img_file(r, i) for i, r in enumerate(reports)]
        with caplog.at_level(logging.WARNING, logger="echo_extractor.images"):
            pages = filter_report_pages(imgs)
        assert len(pages) == 2
        assert any("expected 4 report pages" in m for m in caplog.messages)

    def test_all_four_report_pages(self, tmp_path):
        reports = [_make_tif(tmp_path / f"r{i}.tif", REPORT_SIZE) for i in range(4)]
        imgs = [_img_file(r, i) for i, r in enumerate(reports)]
        pages = filter_report_pages(imgs)
        assert len(pages) == 4
