"""Tests for Pydantic schema validation and column mapping."""
import json
import pytest
from pydantic import ValidationError

from echo_extractor.schema import ALWAYS_BLANK, COLUMN_MAP, EchoData


class TestEchoDataValidation:
    def test_fully_populated_round_trips(self):
        payload = {
            "age": 65.0, "agestring": "65Years", "sex": "M",
            "height": 170.0, "weight": 75.0, "bsa": 1.87,
            "savedate": "2025-04-02", "indication": "Hypertension",
            "ivsd": 10.5, "lvidd": 50.0, "lvpwd": 10.0,
            "lvids": 32.0, "ef": 62.0, "fs": 35.0,
            "edv": 120.0, "esv": 45.0, "sv": 75.0, "si": 40.0,
            "mv_e": 0.82, "mv_a": 0.65, "e_a": 1.26,
            "av_vmax": 1.2, "av_pgmax": 5.8,
            "tr_vmax": 2.5, "tr_pgmax": 25.0, "rap": 5.0, "rsvp": 30.0,
            "aod": 34.0, "las_diam": 38.0, "aod_las": 0.89,
            "tapse": 22.0,
        }
        data = EchoData.model_validate(payload)
        assert data.age == 65.0
        assert data.sex == "M"
        assert data.ef == 62.0

    def test_all_none_is_valid(self):
        data = EchoData.model_validate({})
        for field in EchoData.model_fields:
            assert getattr(data, field) is None

    def test_partial_data_leaves_rest_none(self):
        data = EchoData.model_validate({"ef": 55.0, "tapse": 18.0})
        assert data.ef == 55.0
        assert data.tapse == 18.0
        assert data.ivsd is None
        assert data.av_vmax is None

    def test_null_in_json_becomes_none(self):
        raw = '{"age": null, "ef": 62.0}'
        data = EchoData.model_validate_json(raw)
        assert data.age is None
        assert data.ef == 62.0

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            EchoData.model_validate({"ef": "not-a-number"})

    def test_json_schema_is_serialisable(self):
        schema = EchoData.model_json_schema()
        dumped = json.dumps(schema)
        assert "ef" in dumped
        assert "age" in dumped


class TestColumnMap:
    def test_all_map_keys_are_schema_fields(self):
        schema_fields = set(EchoData.model_fields.keys())
        for key in COLUMN_MAP:
            assert key in schema_fields, f"{key!r} in COLUMN_MAP but not in EchoData"

    def test_always_blank_columns_not_in_column_map_targets(self):
        """No COLUMN_MAP entry should target an ALWAYS_BLANK column."""
        targets: set[str] = set()
        for v in COLUMN_MAP.values():
            if isinstance(v, list):
                targets.update(v)
            else:
                targets.add(v)
        overlap = targets & ALWAYS_BLANK
        assert not overlap, f"COLUMN_MAP targets ALWAYS_BLANK columns: {overlap}"

    def test_height_maps_to_multiple_columns(self):
        mapping = COLUMN_MAP["height"]
        assert isinstance(mapping, list)
        assert "height" in mapping
        assert "hoheight" in mapping

    def test_savedate_maps_to_three_columns(self):
        mapping = COLUMN_MAP["savedate"]
        assert isinstance(mapping, list)
        assert len(mapping) == 3
