# Privacy Notes

## What this project collects

Nothing. The toolkit reads local JSON input files and writes results to stdout. It does not collect telemetry, make network requests, or store any data outside the working directory.

## Sample data

All sample files in `samples/` use entirely fake data:

- Hostnames (`DEMO-PC-01`, `DEMO-PC-02`) are placeholders with no relation to real machines
- Service names are standard Windows service names used as examples only
- Event log messages are paraphrased from public Microsoft documentation
- Disk labels and capacities are invented for demonstration purposes

## Before publishing input files

If you create your own input files from real systems, review them before committing. Remove or replace:

- Real hostnames or machine names
- Internal domain names or IP addresses
- Usernames or account names in event log messages
- Any data that could identify individuals or organizations

## Contact

Open a GitHub issue if you have questions about data handling in this project.
