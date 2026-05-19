# Operations Guide

## Test Execution

Use the default suite for local and CI validation:

```bash
python -m pytest
```

Use marker-based selection for targeted checks:

```bash
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest -m negative
```

## Reports

The pytest session hook writes a JSON summary to:

```text
reports/test_summary.json
```

The HTML report command writes:

```text
reports/report.html
```

## Mock Service

Run locally:

```bash
python scripts/init_db.py
python -m mock_service.server
```

Health and metrics:

```bash
curl http://127.0.0.1:8089/health
curl http://127.0.0.1:8089/metrics
```

## Real Environment Checklist

- Point `SCORING_BASE_URL` to the integration environment.
- Keep production credentials outside the repository.
- Replace SQLite adapter behavior in `src/astrascore_qa/db.py` when a real DWH or RDBMS is used.
- Keep regression baselines versioned and reviewed.
- Archive CI artifacts for audit evidence.
