import json
import pytest
from src.service_health import ServiceRecord, load_services, analyze


SAMPLE = [
    {"name": "Spooler",  "state": "Stopped",  "start_type": "Automatic", "pid": None, "host": "HOST-01"},
    {"name": "wuauserv", "state": "Running",  "start_type": "Automatic", "pid": 2344, "host": "HOST-01"},
    {"name": "BITS",     "state": "Stopped",  "start_type": "Manual",    "pid": None, "host": "HOST-01"},
    {"name": "TapiSrv",  "state": "Degraded", "start_type": "Manual",    "pid": 5601, "host": "HOST-01"},
    {"name": "VSS",      "state": "Stopped",  "start_type": "Automatic", "pid": None, "host": "HOST-01"},
]


@pytest.fixture
def services_file(tmp_path):
    f = tmp_path / "services.json"
    f.write_text(json.dumps(SAMPLE))
    return f


def test_load_returns_correct_count(services_file):
    services = load_services(services_file)
    assert len(services) == 5


def test_load_returns_service_records(services_file):
    services = load_services(services_file)
    assert all(isinstance(s, ServiceRecord) for s in services)


def test_analyze_state_counts(services_file):
    result = analyze(load_services(services_file))
    assert result["total"] == 5
    assert result["running"] == 1
    assert result["stopped"] == 3
    assert result["degraded"] == 1


def test_critical_stopped_excludes_manual(services_file):
    result = analyze(load_services(services_file))
    # BITS is Manual — should not count as critical; Spooler and VSS are Automatic
    assert result["critical_stopped"] == 2


def test_high_findings_for_automatic_stopped(services_file):
    result = analyze(load_services(services_file))
    high = [f for f in result["findings"] if f["severity"] == "high"]
    names = {f["service"] for f in high}
    assert "Spooler" in names
    assert "VSS" in names
    assert "BITS" not in names


def test_medium_findings_for_degraded(services_file):
    result = analyze(load_services(services_file))
    med = [f for f in result["findings"] if f["severity"] == "medium"]
    assert any(f["service"] == "TapiSrv" for f in med)


def test_custom_alert_start_types_includes_manual():
    services = [
        ServiceRecord("MySvc",   "Stopped", "Manual",    None, "HOST-01"),
        ServiceRecord("OtherSvc","Stopped", "Automatic", None, "HOST-01"),
    ]
    result = analyze(services, alert_start_types=["Automatic", "Manual"])
    assert result["critical_stopped"] == 2


def test_all_running_produces_no_findings():
    services = [
        ServiceRecord("SvcA", "Running", "Automatic", 100, "HOST-01"),
        ServiceRecord("SvcB", "Running", "Manual",    200, "HOST-01"),
    ]
    result = analyze(services)
    assert result["findings"] == []
    assert result["critical_stopped"] == 0


def test_finding_contains_host_and_detail():
    services = [ServiceRecord("Spooler", "Stopped", "Automatic", None, "HOST-99")]
    result = analyze(services)
    finding = result["findings"][0]
    assert finding["host"] == "HOST-99"
    assert "Spooler" in finding["detail"]


def test_load_malformed_json_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not valid json {")
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_services(f)


def test_load_not_array_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"name": "Spooler"}))
    with pytest.raises(ValueError, match="Expected a JSON array"):
        load_services(f)


def test_load_missing_field_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"name": "Spooler"}]))
    with pytest.raises(ValueError, match="Missing or invalid field"):
        load_services(f)
