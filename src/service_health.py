"""Service health analysis — load structured service records and flag stopped/degraded services."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ServiceRecord:
    name: str
    state: str
    start_type: str
    pid: Optional[int]
    host: str


def load_services(path: Path) -> list[ServiceRecord]:
    try:
        raw = json.loads(Path(path).read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")
    try:
        return [ServiceRecord(**r) for r in raw]
    except TypeError as exc:
        raise ValueError(f"Missing or invalid field in {path}: {exc}") from exc


def analyze(
    services: list[ServiceRecord],
    alert_start_types: list[str] | None = None,
) -> dict:
    if alert_start_types is None:
        alert_start_types = ["Automatic"]

    running = [s for s in services if s.state == "Running"]
    stopped = [s for s in services if s.state == "Stopped"]
    degraded = [s for s in services if s.state == "Degraded"]

    critical_stopped = [s for s in stopped if s.start_type in alert_start_types]

    findings: list[dict] = []
    for svc in critical_stopped:
        findings.append({
            "severity": "high",
            "type": "service_stopped",
            "service": svc.name,
            "host": svc.host,
            "detail": f"'{svc.name}' is stopped but start_type is {svc.start_type} on {svc.host}",
        })
    for svc in degraded:
        findings.append({
            "severity": "medium",
            "type": "service_degraded",
            "service": svc.name,
            "host": svc.host,
            "detail": f"'{svc.name}' is in a degraded state on {svc.host}",
        })

    return {
        "total": len(services),
        "running": len(running),
        "stopped": len(stopped),
        "degraded": len(degraded),
        "critical_stopped": len(critical_stopped),
        "findings": findings,
    }
