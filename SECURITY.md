# Security Policy

## Data safety

This repository is designed to work with sample data only. All hostnames, service names, event log messages, and disk records in `samples/` are fake and safe to publish.

## Do not commit

- API keys or access tokens
- GitHub tokens or CI secrets
- Passwords or credential files
- `.env` files
- Real Windows event logs
- Real disk records with private hostnames
- Customer data of any kind
- Internal IP addresses or private domain names

## Input file handling

The toolkit reads local JSON files. It does not make network requests, write to system registries, or execute shell commands. All sample input files in `samples/` use placeholder hostnames (`DEMO-PC-01`, `DEMO-PC-02`).

## Reporting a concern

If you find content in this repository that appears to contain sensitive or real data, please open a GitHub issue describing what you found. Do not include the sensitive data in the issue body.

## Dependency policy

This project has no runtime dependencies beyond the Python standard library. The only development dependency is `pytest`. Keep the dependency surface minimal.
