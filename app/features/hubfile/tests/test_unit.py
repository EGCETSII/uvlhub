"""Unit tests for the hubfile feature — pure logic, no Flask app, no DB."""

from datetime import datetime, timezone

import pytest

from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord

pytestmark = pytest.mark.unit


def test_formatted_size_reports_raw_bytes_below_one_kilobyte():
    hubfile = Hubfile(name="tiny.uvl", checksum="abc", size=512, feature_model_id=1)
    assert hubfile.get_formatted_size() == "512 bytes"


def test_formatted_size_switches_to_kilobytes_at_the_boundary():
    below = Hubfile(name="a.uvl", checksum="abc", size=1023, feature_model_id=1)
    at = Hubfile(name="b.uvl", checksum="abc", size=1024, feature_model_id=1)
    assert below.get_formatted_size() == "1023 bytes"
    assert at.get_formatted_size() == "1.0 KB"


def test_formatted_size_scales_to_megabytes():
    hubfile = Hubfile(name="big.uvl", checksum="abc", size=5 * 1024**2, feature_model_id=1)
    assert hubfile.get_formatted_size() == "5.0 MB"


def test_hubfile_repr_exposes_the_id():
    hubfile = Hubfile(name="model.uvl", checksum="abc", size=10, feature_model_id=1)
    hubfile.id = 7
    assert repr(hubfile) == "File<7>"


def test_view_record_repr_exposes_the_id():
    record = HubfileViewRecord(file_id=3, view_cookie="cookie-a")
    record.id = 11
    assert repr(record) == "<FileViewRecord 11>"


def test_download_record_repr_exposes_file_and_cookie():
    record = HubfileDownloadRecord(
        file_id=42,
        download_date=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        download_cookie="cookie-b",
    )
    record.id = 9

    text = repr(record)
    assert "id=9" in text
    assert "file_id=42" in text
    assert "cookie=cookie-b" in text
