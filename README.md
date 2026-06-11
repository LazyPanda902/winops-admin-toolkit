# WinOps Admin Toolkit


A command-line toolkit for reviewing Windows system health from structured JSON records. Analyzes service status, event log data, and disk usage — and generates a combined prioritized findings report.

All analysis runs locally against sample or exported JSON input files. No Windows host connection required.

## What it does

| Command | What it analyzes |
|---------|-----------------|
| `services` | Flags services that are stopped when set to start automatically, and services in a degraded state |
| `events` | Counts events by severity level, surfaces top errors and critical events by occurrence count |
| `disks` | Flags volumes above configurable warning and critical usage thresholds |
| `report` | Aggregates findings from all three sources into a single prioritized output |

## Setup

```bash
git clone https://github.com/LazyPanda902/winops-admin-toolkit.git
cd winops-admin-toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Python 3.11+ required. No third-party runtime dependencies. Installing with `pip install -e .` makes the `winops` command available.

## Usage

### Service health

```bash
winops services samples/services.json
winops --json services samples/services.json
```

### Event log

```bash
winops events samples/events.json
winops events samples/events.json --top-n 10
```

### Disk usage

```bash
winops disks samples/disks.json
winops disks samples/disks.json --warning 75 --critical 88
```

### Combined report

```bash
winops report \
  --services samples/services.json \
  --events   samples/events.json \
  --disks    samples/disks.json

# JSON output
winops --json report \
  --services samples/services.json \
  --events   samples/events.json \
  --disks    samples/disks.json

# Write report to file
winops report --services samples/services.json --output-file report.txt
```

The CLI exits with code `1` when any high-severity findings are present, making it usable in shell pipelines.

### Custom config

```bash
winops --config config/default.json report --services samples/services.json
```

See [docs/config-example.md](docs/config-example.md) for all options and input formats.

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=src --cov-fail-under=80
```

The test suite covers all analysis modules, the report builder, and the CLI.

## Project structure

```
src/
  cli.py              CLI entry point — subcommands, flags, config loading
  service_health.py   Load and analyze service status records
  event_log.py        Load and summarize event log records
  disk_usage.py       Load and analyze disk usage records
  report.py           Build and format a combined findings report
tests/                pytest test suite (one file per module)
samples/              Sample JSON input files (fake data only)
config/               Default JSON config
docs/                 Config reference, usage examples, testing guide, roadmap
.github/workflows/    GitHub Actions CI (Python 3.11 and 3.12)
```

## Input format overview

### services.json

```json
[
  {"name": "Spooler", "state": "Stopped", "start_type": "Automatic", "pid": null, "host": "DEMO-PC-01"}
]
```

### events.json

```json
[
  {"event_id": 7034, "level": "Error", "source": "Service Control Manager",
   "message": "Print Spooler stopped.", "timestamp": "2024-01-15T09:23:11Z",
   "host": "DEMO-PC-01", "count": 3}
]
```

### disks.json

```json
[
  {"drive": "C:", "label": "OS", "total_gb": 238.5, "used_gb": 198.2, "free_gb": 40.3, "host": "DEMO-PC-01"}
]
```

## More examples

See [docs/usage-examples.md](docs/usage-examples.md) for full command examples and sample output.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Security

This repository contains only sample data with fake hostnames, service names, and disk labels. Do not commit real event logs, credentials, hostnames, or customer data. See [SECURITY.md](SECURITY.md).

## License

MIT
