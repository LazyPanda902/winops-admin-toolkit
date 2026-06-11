import json
import pytest
from src.cli import main, build_parser, load_config


SERVICES = [
    {"name": "Spooler",  "state": "Stopped", "start_type": "Automatic", "pid": None, "host": "HOST-01"},
    {"name": "wuauserv", "state": "Running", "start_type": "Automatic", "pid": 1234, "host": "HOST-01"},
]
EVENTS = [
    {"event_id": 7034, "level": "Error",       "source": "SCM",    "message": "Service stopped.", "timestamp": "2024-01-01T00:00:00Z", "host": "HOST-01", "count": 2},
    {"event_id": 1074, "level": "Information", "source": "User32", "message": "Started.",         "timestamp": "2024-01-01T00:00:00Z", "host": "HOST-01", "count": 1},
]
DISKS = [
    {"drive": "C:", "label": "OS",   "total_gb": 100.0, "used_gb": 92.0,  "free_gb": 8.0,   "host": "HOST-01"},
    {"drive": "D:", "label": "Data", "total_gb": 500.0, "used_gb": 200.0, "free_gb": 300.0, "host": "HOST-01"},
]


@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "services.json").write_text(json.dumps(SERVICES))
    (tmp_path / "events.json").write_text(json.dumps(EVENTS))
    (tmp_path / "disks.json").write_text(json.dumps(DISKS))
    return tmp_path


def test_services_json_output(sample_dir, capsys):
    rc = main(["--json", "services", str(sample_dir / "services.json")])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 2
    assert data["stopped"] == 1
    assert data["critical_stopped"] == 1


def test_events_json_output(sample_dir, capsys):
    rc = main(["--json", "events", str(sample_dir / "events.json")])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_events"] == 3


def test_disks_json_output(sample_dir, capsys):
    rc = main(["--json", "disks", str(sample_dir / "disks.json")])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_volumes"] == 2


def test_disks_critical_threshold_flag(sample_dir, capsys):
    main(["--json", "disks", str(sample_dir / "disks.json"), "--critical", "85"])
    data = json.loads(capsys.readouterr().out)
    # C: is 92% → critical at threshold 85
    assert data["critical_count"] == 1


def test_disks_warning_threshold_flag(sample_dir, capsys):
    main(["--json", "disks", str(sample_dir / "disks.json"), "--warning", "70", "--critical", "95"])
    data = json.loads(capsys.readouterr().out)
    # C: is 92% → warning when critical is 95
    assert data["warning_count"] == 1


def test_events_top_n_flag(sample_dir, capsys):
    main(["--json", "events", str(sample_dir / "events.json"), "--top-n", "1"])
    data = json.loads(capsys.readouterr().out)
    assert len(data["top_errors"]) <= 1


def test_report_json_output(sample_dir, capsys):
    rc = main([
        "--json", "report",
        "--services", str(sample_dir / "services.json"),
        "--events", str(sample_dir / "events.json"),
        "--disks", str(sample_dir / "disks.json"),
    ])
    data = json.loads(capsys.readouterr().out)
    assert "overall_status" in data
    assert data["finding_counts"]["total"] >= 1


def test_report_text_output_contains_header(sample_dir, capsys):
    main(["report", "--services", str(sample_dir / "services.json")])
    out = capsys.readouterr().out
    assert "WinOps Admin Toolkit" in out


def test_report_exits_1_on_critical(sample_dir, capsys):
    rc = main(["report", "--services", str(sample_dir / "services.json")])
    capsys.readouterr()
    assert rc == 1


def test_load_config_returns_defaults_when_no_file():
    cfg = load_config(None)
    assert cfg["disk_usage"]["warning_percent"] == 80.0
    assert cfg["disk_usage"]["critical_percent"] == 90.0
    assert cfg["event_log"]["top_n"] == 5
    assert "Automatic" in cfg["services"]["alert_start_types"]


def test_load_config_overrides_from_file(tmp_path):
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps({"disk_usage": {"warning_percent": 70.0}}))
    cfg = load_config(cfg_file)
    assert cfg["disk_usage"]["warning_percent"] == 70.0
    assert cfg["disk_usage"]["critical_percent"] == 90.0  # default preserved


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_malformed_json_exits_2(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json {")
    rc = main(["services", str(bad)])
    assert rc == 2


def test_missing_field_exits_2(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"name": "Svc"}]))
    rc = main(["services", str(bad)])
    assert rc == 2


def test_report_output_file_text(sample_dir, tmp_path):
    out = tmp_path / "report.txt"
    main(["report", "--services", str(sample_dir / "services.json"), "--output-file", str(out)])
    assert out.exists()
    assert "WinOps Admin Toolkit" in out.read_text()


def test_report_output_file_json(sample_dir, tmp_path):
    out = tmp_path / "report.json"
    main(["--json", "report", "--services", str(sample_dir / "services.json"), "--output-file", str(out)])
    assert out.exists()
    data = json.loads(out.read_text())
    assert "overall_status" in data
