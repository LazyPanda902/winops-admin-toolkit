"""Disk usage analysis — load volume records and flag drives above usage thresholds."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiskRecord:
    drive: str
    label: str
    total_gb: float
    used_gb: float
    free_gb: float
    host: str

    @property
    def used_percent(self) -> float:
        if self.total_gb == 0:
            return 0.0
        return round(self.used_gb / self.total_gb * 100, 1)


def load_disks(path: Path) -> list[DiskRecord]:
    try:
        raw = json.loads(Path(path).read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")
    try:
        return [DiskRecord(**r) for r in raw]
    except TypeError as exc:
        raise ValueError(f"Missing or invalid field in {path}: {exc}") from exc


def analyze(
    disks: list[DiskRecord],
    warning_percent: float = 80.0,
    critical_percent: float = 90.0,
) -> dict:
    findings: list[dict] = []
    critical_count = 0
    warning_count = 0

    for disk in disks:
        pct = disk.used_percent
        if pct >= critical_percent:
            critical_count += 1
            findings.append({
                "severity": "high",
                "type": "disk_critical",
                "drive": disk.drive,
                "host": disk.host,
                "used_percent": pct,
                "free_gb": disk.free_gb,
                "detail": (
                    f"{disk.host}:{disk.drive} ({disk.label}) is {pct}% full "
                    f"— only {disk.free_gb:.1f} GB free"
                ),
            })
        elif pct >= warning_percent:
            warning_count += 1
            findings.append({
                "severity": "medium",
                "type": "disk_warning",
                "drive": disk.drive,
                "host": disk.host,
                "used_percent": pct,
                "free_gb": disk.free_gb,
                "detail": (
                    f"{disk.host}:{disk.drive} ({disk.label}) is {pct}% full "
                    f"— {disk.free_gb:.1f} GB free"
                ),
            })

    return {
        "total_volumes": len(disks),
        "critical_count": critical_count,
        "warning_count": warning_count,
        "total_capacity_gb": round(sum(d.total_gb for d in disks), 1),
        "total_used_gb": round(sum(d.used_gb for d in disks), 1),
        "total_free_gb": round(sum(d.free_gb for d in disks), 1),
        "volumes": [
            {
                "drive": d.drive,
                "host": d.host,
                "label": d.label,
                "total_gb": d.total_gb,
                "used_gb": d.used_gb,
                "free_gb": d.free_gb,
                "used_percent": d.used_percent,
            }
            for d in disks
        ],
        "findings": findings,
    }
