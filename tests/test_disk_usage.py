import json
import pytest
from src.disk_usage import DiskRecord, load_disks, analyze


SAMPLE = [
    {"drive": "C:", "label": "OS",     "total_gb": 238.5,  "used_gb": 198.2, "free_gb": 40.3,  "host": "HOST-01"},
    {"drive": "D:", "label": "Data",   "total_gb": 500.0,  "used_gb": 475.0, "free_gb": 25.0,  "host": "HOST-01"},
    {"drive": "E:", "label": "Backup", "total_gb": 1000.0, "used_gb": 550.0, "free_gb": 450.0, "host": "HOST-01"},
]


@pytest.fixture
def disks_file(tmp_path):
    f = tmp_path / "disks.json"
    f.write_text(json.dumps(SAMPLE))
    return f


def test_load_returns_correct_count(disks_file):
    disks = load_disks(disks_file)
    assert len(disks) == 3


def test_load_returns_disk_records(disks_file):
    disks = load_disks(disks_file)
    assert all(isinstance(d, DiskRecord) for d in disks)


def test_used_percent_property():
    disk = DiskRecord("C:", "OS", 100.0, 83.0, 17.0, "HOST")
    assert disk.used_percent == 83.0


def test_zero_capacity_returns_zero_percent():
    disk = DiskRecord("X:", "Empty", 0.0, 0.0, 0.0, "HOST")
    assert disk.used_percent == 0.0


def test_critical_drive_detected(disks_file):
    result = analyze(load_disks(disks_file), warning_percent=80.0, critical_percent=90.0)
    # D: is 475/500 = 95% → critical
    assert result["critical_count"] == 1
    critical = [f for f in result["findings"] if f["severity"] == "high"]
    assert critical[0]["drive"] == "D:"


def test_warning_drive_detected(disks_file):
    result = analyze(load_disks(disks_file), warning_percent=80.0, critical_percent=90.0)
    # C: is 198.2/238.5 ≈ 83.1% → warning
    warning = [f for f in result["findings"] if f["severity"] == "medium"]
    assert any(f["drive"] == "C:" for f in warning)


def test_ok_drive_produces_no_finding(disks_file):
    result = analyze(load_disks(disks_file), warning_percent=80.0, critical_percent=90.0)
    # E: is 550/1000 = 55% → ok
    finding_drives = {f["drive"] for f in result["findings"]}
    assert "E:" not in finding_drives


def test_totals_calculated(disks_file):
    result = analyze(load_disks(disks_file))
    assert result["total_volumes"] == 3
    assert result["total_capacity_gb"] == pytest.approx(1738.5, abs=0.1)
    assert result["total_free_gb"] == pytest.approx(515.3, abs=0.1)


def test_volumes_list_populated(disks_file):
    result = analyze(load_disks(disks_file))
    assert len(result["volumes"]) == 3
    drives = {v["drive"] for v in result["volumes"]}
    assert drives == {"C:", "D:", "E:"}


def test_custom_thresholds_change_classifications():
    disks = [DiskRecord("C:", "OS", 100.0, 75.0, 25.0, "HOST")]
    result_default = analyze(disks, warning_percent=80.0)
    result_lower = analyze(disks, warning_percent=70.0)
    assert result_default["warning_count"] == 0
    assert result_lower["warning_count"] == 1


def test_load_malformed_json_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("{ broken json")
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_disks(f)


def test_load_not_array_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"drive": "C:"}))
    with pytest.raises(ValueError, match="Expected a JSON array"):
        load_disks(f)


def test_load_missing_field_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"drive": "C:"}]))
    with pytest.raises(ValueError, match="Missing or invalid field"):
        load_disks(f)
