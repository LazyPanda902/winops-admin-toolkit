"""Event log summarization — load event records and surface top errors by severity and count."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EventRecord:
    event_id: int
    level: str
    source: str
    message: str
    timestamp: str
    host: str
    count: int = 1


def load_events(path: Path) -> list[EventRecord]:
    try:
        raw = json.loads(Path(path).read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")
    try:
        return [EventRecord(**r) for r in raw]
    except TypeError as exc:
        raise ValueError(f"Missing or invalid field in {path}: {exc}") from exc


def summarize(
    events: list[EventRecord],
    top_n: int = 5,
    error_levels: list[str] | None = None,
) -> dict:
    if error_levels is None:
        error_levels = ["Error", "Critical"]

    by_level: dict[str, int] = {}
    for evt in events:
        by_level[evt.level] = by_level.get(evt.level, 0) + evt.count

    total = sum(evt.count for evt in events)

    errors = [e for e in events if e.level in error_levels]
    top_errors = sorted(errors, key=lambda e: e.count, reverse=True)[:top_n]

    findings: list[dict] = []
    for evt in top_errors:
        severity = "high" if evt.level == "Critical" else "medium"
        snippet = evt.message[:80] + ("..." if len(evt.message) > 80 else "")
        findings.append({
            "severity": severity,
            "type": "event_log_error",
            "event_id": evt.event_id,
            "source": evt.source,
            "host": evt.host,
            "count": evt.count,
            "detail": f"Event {evt.event_id} from '{evt.source}' occurred {evt.count}x: {snippet}",
        })

    return {
        "total_events": total,
        "by_level": by_level,
        "top_errors": [asdict(e) for e in top_errors],
        "findings": findings,
    }
