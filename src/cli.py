"""CLI entry point — subcommands for services, events, disks, and combined report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def load_config(config_path: Optional[Path]) -> dict:
    defaults: dict = {
        "disk_usage": {"warning_percent": 80.0, "critical_percent": 90.0},
        "event_log": {"top_n": 5, "error_levels": ["Error", "Critical"]},
        "services": {"alert_start_types": ["Automatic"]},
    }
    if config_path and Path(config_path).exists():
        user_cfg = json.loads(Path(config_path).read_text())
        for section, values in user_cfg.items():
            if section in defaults and isinstance(values, dict):
                defaults[section].update(values)
            else:
                defaults[section] = values
    return defaults


def _output(data: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2))
        return
    for key, value in data.items():
        if key == "findings":
            print(f"\nFindings ({len(value)}):")
            for f in value:
                sev = f.get("severity", "?").upper()
                print(f"  [{sev}] {f.get('detail', f.get('type', ''))}")
        elif key == "volumes":
            print("Volumes:")
            for v in value:
                print(f"  {v['host']}:{v['drive']} ({v['label']})  {v['used_percent']}% used  {v['free_gb']:.1f} GB free")
        elif key == "top_errors":
            if value:
                print(f"\nTop Errors ({len(value)}):")
                for e in value:
                    level = e.get("level", "?").upper()
                    eid = e.get("event_id", "?")
                    src = e.get("source", "?")
                    host = e.get("host", "?")
                    cnt = e.get("count", 1)
                    print(f"  [{level}] Event {eid} from '{src}' on {host} — {cnt}x")
        elif isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, list):
            if value:
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
        else:
            print(f"{key}: {value}")


def cmd_services(args: argparse.Namespace, cfg: dict) -> int:
    from src import service_health

    services = service_health.load_services(Path(args.input))
    result = service_health.analyze(
        services,
        alert_start_types=cfg["services"]["alert_start_types"],
    )
    _output(result, args.json)
    return 0


def cmd_events(args: argparse.Namespace, cfg: dict) -> int:
    from src import event_log

    events = event_log.load_events(Path(args.input))
    result = event_log.summarize(
        events,
        top_n=args.top_n if args.top_n is not None else cfg["event_log"]["top_n"],
        error_levels=cfg["event_log"]["error_levels"],
    )
    _output(result, args.json)
    return 0


def cmd_disks(args: argparse.Namespace, cfg: dict) -> int:
    from src import disk_usage

    disks = disk_usage.load_disks(Path(args.input))
    result = disk_usage.analyze(
        disks,
        warning_percent=args.warning if args.warning is not None else cfg["disk_usage"]["warning_percent"],
        critical_percent=args.critical if args.critical is not None else cfg["disk_usage"]["critical_percent"],
    )
    _output(result, args.json)
    return 0


def cmd_report(args: argparse.Namespace, cfg: dict) -> int:
    from src import service_health, event_log, disk_usage, report

    svc_result = None
    evt_result = None
    dsk_result = None

    if getattr(args, "services", None):
        svc_result = service_health.analyze(
            service_health.load_services(Path(args.services)),
            alert_start_types=cfg["services"]["alert_start_types"],
        )
    if getattr(args, "events", None):
        evt_result = event_log.summarize(
            event_log.load_events(Path(args.events)),
            top_n=cfg["event_log"]["top_n"],
            error_levels=cfg["event_log"]["error_levels"],
        )
    if getattr(args, "disks", None):
        dsk_result = disk_usage.analyze(
            disk_usage.load_disks(Path(args.disks)),
            warning_percent=cfg["disk_usage"]["warning_percent"],
            critical_percent=cfg["disk_usage"]["critical_percent"],
        )

    result = report.build_report(svc_result, evt_result, dsk_result)
    output = json.dumps(result, indent=2) if args.json else report.format_text_report(result)

    output_file = getattr(args, "output_file", None)
    if output_file:
        Path(output_file).write_text(output)
    else:
        print(output)

    return 1 if result["overall_status"] == "critical" else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="winops",
        description="Windows admin support toolkit — service health, event logs, disk usage.",
    )
    parser.add_argument("--config", metavar="PATH", help="JSON config file (default: config/default.json)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    p_svc = sub.add_parser("services", help="Review Windows service health")
    p_svc.add_argument("input", help="Path to services JSON input file")

    p_evt = sub.add_parser("events", help="Summarize Windows event log records")
    p_evt.add_argument("input", help="Path to events JSON input file")
    p_evt.add_argument("--top-n", type=int, default=None, metavar="N", dest="top_n", help="Number of top errors to report")

    p_dsk = sub.add_parser("disks", help="Analyze disk usage records")
    p_dsk.add_argument("input", help="Path to disks JSON input file")
    p_dsk.add_argument("--warning", type=float, default=None, metavar="PCT", help="Warning threshold percent")
    p_dsk.add_argument("--critical", type=float, default=None, metavar="PCT", help="Critical threshold percent")

    p_rep = sub.add_parser("report", help="Generate combined support findings report")
    p_rep.add_argument("--services", metavar="PATH", help="Path to services JSON input")
    p_rep.add_argument("--events", metavar="PATH", help="Path to events JSON input")
    p_rep.add_argument("--disks", metavar="PATH", help="Path to disks JSON input")
    p_rep.add_argument("--output-file", metavar="PATH", dest="output_file", help="Write report to file instead of stdout")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config) if args.config else Path("config/default.json")
    cfg = load_config(config_path)

    handlers = {
        "services": cmd_services,
        "events": cmd_events,
        "disks": cmd_disks,
        "report": cmd_report,
    }
    try:
        return handlers[args.command](args, cfg)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
