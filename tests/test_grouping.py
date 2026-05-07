"""Tests for filename parsing and patient grouping."""
import pytest
from pathlib import Path
from echo_extractor.grouping import parse_filename, group_by_patient


def _fake(name: str) -> Path:
    return Path(f"/tmp/{name}")


class TestParseFilename:
    def test_actual_format(self):
        p = parse_filename(_fake("J00088936NHIF_02.04.2025.17.07.12_22.tif"))
        assert p is not None
        assert p.patient_id == "J00088936NHIF"
        assert p.image_num == 22
        assert p.exam_id is None

    def test_spec_format(self):
        p = parse_filename(_fake("1778140551195_J00088936NHIF_02_04_2025_17_07_12_2.tif"))
        assert p is not None
        assert p.patient_id == "J00088936NHIF"
        assert p.exam_id == "1778140551195"
        assert p.image_num == 2

    def test_non_tif_returns_none(self):
        assert parse_filename(_fake("J00088936NHIF_02.04.2025.17.07.12_22.png")) is None

    def test_garbled_name_returns_none(self):
        assert parse_filename(_fake("no_segments.tif")) is None

    def test_image_num_parsed_correctly(self):
        for num in [2, 10, 22, 25]:
            p = parse_filename(_fake(f"PAT001_01.01.2025.12.00.00_{num}.tif"))
            assert p is not None and p.image_num == num


class TestGroupByPatient:
    def test_groups_multiple_images_by_patient(self, tmp_path):
        for num in [2, 3, 22, 23]:
            (tmp_path / f"PAT001_01.01.2025.12.00.00_{num}.tif").touch()
        for num in [4, 24]:
            (tmp_path / f"PAT002_01.01.2025.12.00.00_{num}.tif").touch()
        groups = group_by_patient(tmp_path)
        assert set(groups.keys()) == {"PAT001", "PAT002"}
        assert [f.image_num for f in groups["PAT001"]] == [2, 3, 22, 23]
        assert [f.image_num for f in groups["PAT002"]] == [4, 24]

    def test_ignores_non_tif(self, tmp_path):
        (tmp_path / "PAT001_01.01.2025.12.00.00_1.tif").touch()
        (tmp_path / "notes.txt").touch()
        groups = group_by_patient(tmp_path)
        assert list(groups.keys()) == ["PAT001"]
