# Roadmap

## Shipped

- Service health review — flag stopped/degraded services by configurable start type
- Event log summarization — count by severity, surface top errors with occurrence counts
- Disk usage analysis — flag volumes above configurable warning and critical thresholds
- Combined support findings report with text and JSON output
- CLI with subcommands (`services`, `events`, `disks`, `report`), `--json` flag, and `--config` support
- Config file support with per-section threshold overrides
- Sample JSON input files (fake data, safe to publish)
- pytest test suite covering all analysis modules, the report builder, and the CLI
- GitHub Actions CI on Python 3.11 and 3.12 with ruff lint and 80% coverage gate
- `--output-file` flag to write the report to a file instead of stdout
- JSON input validation with clear error messages for malformed or missing-field input
- `winops` CLI entry point via `pip install -e .`

## Planned

### Near-term

- CSV input support for event logs exported from Windows Event Viewer
- Multi-host report aggregation — combine input from several machines into one report
- `--filter-host` flag to scope analysis to a single hostname

### Medium-term

- HTML report output with sortable findings table
- Severity summary diff — compare two report snapshots to show what changed
- Configurable finding suppression — ignore known/expected service states

### Long-term

- Remote input collection via SSH or WinRM (read-only, no-op mode for safe testing)
- Integration with Windows Performance Monitor counter log exports
- Scheduled health checks with configurable polling interval and change alerting
