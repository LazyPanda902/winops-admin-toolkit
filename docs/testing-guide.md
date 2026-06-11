# Testing

Install dependencies and run tests:

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=src --cov-fail-under=80
```

CI runs on every push and pull request across Python 3.11 and 3.12. See `.github/workflows/ci.yml`.
