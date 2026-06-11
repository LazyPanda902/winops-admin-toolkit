import json
import pytest
from src.event_log import EventRecord, load_events, summarize


SAMPLE = [
    {"event_id": 7034,  "level": "Error",       "source": "SCM",          "message": "Print Spooler stopped.",   "timestamp": "2024-01-15T09:23:11Z", "host": "HOST-01", "count": 3},
    {"event_id": 41,    "level": "Critical",     "source": "Kernel-Power", "message": "Unexpected reboot.",       "timestamp": "2024-01-14T23:01:55Z", "host": "HOST-01", "count": 1},
    {"event_id": 10016, "level": "Error",        "source": "DCOM",         "message": "COM permission denied.",   "timestamp": "2024-01-15T09:15:30Z", "host": "HOST-01", "count": 12},
    {"event_id": 36,    "level": "Warning",      "source": "W32Time",      "message": "Time sync lag.",           "timestamp": "2024-01-15T07:00:00Z", "host": "HOST-01", "count": 2},
    {"event_id": 1074,  "level": "Information",  "source": "User32",       "message": "System restarted.",        "timestamp": "2024-01-15T07:29:55Z", "host": "HOST-01", "count": 1},
]


@pytest.fixture
def events_file(tmp_path):
    f = tmp_path / "events.json"
    f.write_text(json.dumps(SAMPLE))
    return f


def test_load_returns_correct_count(events_file):
    events = load_events(events_file)
    assert len(events) == 5


def test_load_returns_event_records(events_file):
    events = load_events(events_file)
    assert all(isinstance(e, EventRecord) for e in events)


def test_total_events_sums_counts(events_file):
    result = summarize(load_events(events_file))
    assert result["total_events"] == 19  # 3+1+12+2+1


def test_by_level_distribution(events_file):
    result = summarize(load_events(events_file))
    assert result["by_level"]["Error"] == 15      # 3+12
    assert result["by_level"]["Critical"] == 1
    assert result["by_level"]["Warning"] == 2
    assert result["by_level"]["Information"] == 1


def test_top_errors_sorted_descending_by_count(events_file):
    result = summarize(load_events(events_file), top_n=3)
    counts = [e["count"] for e in result["top_errors"]]
    assert counts == sorted(counts, reverse=True)
    assert result["top_errors"][0]["event_id"] == 10016  # 12 occurrences


def test_top_n_limits_output(events_file):
    result = summarize(load_events(events_file), top_n=1)
    assert len(result["top_errors"]) == 1


def test_critical_event_maps_to_high_severity(events_file):
    result = summarize(load_events(events_file))
    high_findings = [f for f in result["findings"] if f["severity"] == "high"]
    assert any(f["event_id"] == 41 for f in high_findings)


def test_error_event_maps_to_medium_severity(events_file):
    result = summarize(load_events(events_file))
    med_findings = [f for f in result["findings"] if f["severity"] == "medium"]
    assert any(f["event_id"] == 10016 for f in med_findings)


def test_custom_error_levels_includes_only_specified():
    events = [
        EventRecord(1, "Warning",     "src", "msg", "2024-01-01T00:00:00Z", "HOST", 5),
        EventRecord(2, "Information", "src", "msg", "2024-01-01T00:00:00Z", "HOST", 1),
    ]
    result = summarize(events, error_levels=["Warning"])
    assert len(result["findings"]) == 1
    assert result["findings"][0]["event_id"] == 1


def test_finding_detail_contains_event_id_and_source(events_file):
    result = summarize(load_events(events_file))
    finding = result["findings"][0]
    assert str(finding["event_id"]) in finding["detail"]
    assert finding["source"] in finding["detail"]


def test_load_malformed_json_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json at all")
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_events(f)


def test_load_not_array_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"event_id": 1}))
    with pytest.raises(ValueError, match="Expected a JSON array"):
        load_events(f)


def test_load_missing_field_raises_value_error(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"event_id": 1}]))
    with pytest.raises(ValueError, match="Missing or invalid field"):
        load_events(f)
