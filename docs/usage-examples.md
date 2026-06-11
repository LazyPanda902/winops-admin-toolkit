# Usage Examples

## Setup

```bash
git clone https://github.com/LazyPanda902/winops-admin-toolkit.git
cd winops-admin-toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

This installs the `winops` command.

---

## Service health review

Check for stopped services that should be running automatically:

```bash
winops services samples/services.json
winops --json services samples/services.json
```

Example JSON output:

```json
{
  "total": 10,
  "running": 6,
  "stopped": 3,
  "degraded": 1,
  "critical_stopped": 2,
  "findings": [
    {
      "severity": "high",
      "type": "service_stopped",
      "service": "Spooler",
      "host": "DEMO-PC-01",
      "detail": "'Spooler' is stopped but start_type is Automatic on DEMO-PC-01"
    }
  ]
}
```

---

## Event log summary

Summarize error and critical events from a log export:

```bash
winops events samples/events.json
winops events samples/events.json --top-n 10
winops --json events samples/events.json
```

---

## Disk usage analysis

Flag volumes above thresholds:

```bash
winops disks samples/disks.json
winops disks samples/disks.json --warning 75 --critical 88
winops --json disks samples/disks.json
```

---

## Combined support report

Aggregate findings from all three sources:

```bash
winops report \
  --services samples/services.json \
  --events   samples/events.json \
  --disks    samples/disks.json
```

Write the report to a file instead of stdout:

```bash
winops report \
  --services samples/services.json \
  --events   samples/events.json \
  --disks    samples/disks.json \
  --output-file report.txt

# JSON report to file
winops --json report \
  --services samples/services.json \
  --output-file report.json
```

The CLI exits with code `1` when any high-severity findings are present, making it usable in shell pipelines.

---

## Custom config

```bash
winops --config config/default.json report --services samples/services.json
```

See [docs/config-example.md](config-example.md) for all available options.
