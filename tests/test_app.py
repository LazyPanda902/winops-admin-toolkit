"""Smoke tests — verify the package imports cleanly and version is set."""

import src.app as app
import src.service_health as service_health
import src.event_log as event_log
import src.disk_usage as disk_usage
import src.report as report
import src.cli as cli


def test_version_is_set():
    assert isinstance(app.__version__, str)
    assert len(app.__version__) > 0


def test_modules_importable():
    assert hasattr(service_health, "analyze")
    assert hasattr(event_log, "summarize")
    assert hasattr(disk_usage, "analyze")
    assert hasattr(report, "build_report")
    assert hasattr(cli, "main")
