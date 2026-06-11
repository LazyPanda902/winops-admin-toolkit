# Configuration Reference

WinOps Admin Toolkit reads a JSON config file to control analysis thresholds and behavior.

## Default location

```
config/default.json
```

Pass a custom config with `--config`:

```bash
python -m src.cli --config path/to/my-config.json services samples/services.json
```

## Full example

```json
{
  "disk_usage": {
    "warning_percent": 80,
    "critical_percent": 90
  },
  "event_log": {
    "top_n": 5,
    "error_levels": ["Error", "Critical"]
  },
  "services": {
    "alert_start_types": ["Automatic"]
  },
  "output": {
    "timestamp_format": "%Y-%m-%dT%H:%M:%SZ"
  }
}
```

## Options

### `disk_usage`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `warning_percent` | float | `80` | Flag volumes at or above this percentage as warnings |
| `critical_percent` | float | `90` | Flag volumes at or above this percentage as critical |

### `event_log`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `top_n` | int | `5` | Maximum number of top errors to include in findings |
| `error_levels` | list | `["Error", "Critical"]` | Event levels treated as errors |

### `services`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `alert_start_types` | list | `["Automatic"]` | Stopped services with these start types are flagged as high severity |

## Input file formats

All input files use JSON arrays. See `samples/` for ready-to-use examples.

### services.json

```json
[
  {"name": "Spooler", "state": "Stopped", "start_type": "Automatic", "pid": null, "host": "DEMO-PC-01"}
]
```

`state` values: `Running`, `Stopped`, `Degraded`
`start_type` values: `Automatic`, `Manual`, `Disabled`

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
