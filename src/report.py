"""Combined support findings report — aggregate results from all analysis modules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def build_report(
    services_result: Optional[dict] = None,
    events_result: Optional[dict] = None,
    disks_result: Optional[dict] = None,
) -> dict:
    all_findings: list[dict] = []
    for section in (services_result, events_result, disks_result):
        if section:
            all_findings.extend(section.get("findings", []))

    high = [f for f in all_findings if f.get("severity") == "high"]
    medium = [f for f in all_findings if f.get("severity") == "medium"]
    low = [f for f in all_findings if f.get("severity") == "low"]

    if high:
        overall_status = "critical"
    elif medium:
        overall_status = "warning"
    else:
        overall_status = "ok"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "finding_counts": {
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "total": len(all_findings),
        },
        "sections": {
            "services": services_result,
            "events": events_result,
            "disks": disks_result,
        },
        "findings": all_findings,
    }


def format_text_report(report: dict) -> str:
    lines = [
        "=" * 60,
        "WinOps Admin Toolkit — Support Findings Report",
        f"Generated : {report['generated_at']}",
        f"Status    : {report['overall_status'].upper()}",
    ]
    counts = report["finding_counts"]
    lines.append(
        f"Findings  : {counts['total']} total  "
        f"({counts['high']} high / {counts['medium']} medium / {counts['low']} low)"
    )
    lines.append("=" * 60)

    if not report["findings"]:
        lines.append("No issues found.")
        return "\n".join(lines)

    for label, key in [("HIGH", "high"), ("MEDIUM", "medium"), ("LOW", "low")]:
        group = [f for f in report["findings"] if f.get("severity") == key]
        if not group:
            continue
        lines.append(f"\n[{label}]")
        for finding in group:
            lines.append(f"  - {finding.get('detail', finding.get('type', ''))}")

    return "\n".join(lines)
