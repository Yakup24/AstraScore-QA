# Contributing

Thanks for improving AstraScore QA.

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
ruff check .
python -m pytest
```

## Pull Request Rules

- Keep changes scoped and testable.
- Add or update tests for behavior changes.
- Do not commit generated reports, local databases, logs, caches, or virtual environments.
- Do not include production customer data or secrets.
- Update `README.md` or `docs/` when behavior changes.

## Security Changes

For security-sensitive updates, include:

- affected surface area
- exploitability notes
- mitigation or detection strategy
- validation command output
