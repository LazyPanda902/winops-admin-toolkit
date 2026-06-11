import pytest
from src.report import build_report, format_text_report


def svc(findings=None):
    return {"total": 5, "running": 3, "stopped": 2, "degraded": 0, "findings": findings or []}


def dsk(findings=None):
    return {"total_volumes": 3, "critical_count": 0, "warning_count": 0, "findings": findings or []}


def evt(findings=None):
    return {"total_events": 10, "by_level": {}, "findings": findings or []}


def high_finding(detail="Service stopped"):
    return {"severity": "high", "type": "service_stopped", "detail": detail}


def medium_finding(detail="Disk at 85%"):
    return {"severity": "medium", "type": "disk_warning", "detail": detail}


def test_no_findings_returns_ok():
    result = build_report(services_result=svc(), disks_result=dsk())
    assert result["overall_status"] == "ok"
    assert result["finding_counts"]["total"] == 0


def test_high_finding_returns_critical():
    result = build_report(services_result=svc([high_finding()]))
    assert result["overall_status"] == "critical"
    assert result["finding_counts"]["high"] == 1


def test_only_medium_returns_warning():
    result = build_report(disks_result=dsk([medium_finding()]))
    assert result["overall_status"] == "warning"
    assert result["finding_counts"]["medium"] == 1


def test_aggregates_findings_from_all_sections():
    result = build_report(
        services_result=svc([high_finding()]),
        events_result=evt([medium_finding()]),
        disks_result=dsk([medium_finding("Disk C: warning")]),
    )
    assert result["finding_counts"]["total"] == 3
    assert result["finding_counts"]["high"] == 1
    assert result["finding_counts"]["medium"] == 2


def test_none_sections_are_accepted():
    result = build_report()
    assert result["overall_status"] == "ok"
    assert result["sections"]["services"] is None
    assert result["sections"]["events"] is None
    assert result["sections"]["disks"] is None


def test_report_has_generated_at_timestamp():
    result = build_report()
    assert "generated_at" in result
    assert "T" in result["generated_at"]


def test_format_text_contains_header():
    result = build_report()
    text = format_text_report(result)
    assert "WinOps Admin Toolkit" in text
    assert "Support Findings Report" in text


def test_format_text_no_findings_message():
    result = build_report()
    text = format_text_report(result)
    assert "No issues found" in text


def test_format_text_shows_critical_status():
    result = build_report(services_result=svc([high_finding("Spooler stopped on HOST-01")]))
    text = format_text_report(result)
    assert "CRITICAL" in text
    assert "Spooler" in text


def test_format_text_groups_by_severity():
    result = build_report(
        services_result=svc([high_finding("High issue")]),
        disks_result=dsk([medium_finding("Medium issue")]),
    )
    text = format_text_report(result)
    assert "[HIGH]" in text
    assert "[MEDIUM]" in text
    assert "High issue" in text
    assert "Medium issue" in text
