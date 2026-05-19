# Changelog

## 2.1.0 - AstraScore QA Launch

- Rebranded the project as AstraScore QA.
- Renamed the Python package to `astrascore_qa`.
- Added MIT license.
- Added `pyproject.toml` metadata and tool configuration.
- Added `requirements-dev.txt`.
- Added Security workflow with CodeQL, Bandit, pip-audit, detect-secrets inventory, and Gitleaks.
- Added Dependabot configuration for Python and GitHub Actions.
- Added `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, CODEOWNERS, issue templates, and PR template.
- Rewrote README and architecture docs for public GitHub presentation.
- Added security and operations docs.

## 2.0.0 - Enterprise Upgrade

- Added config validation and environment override checks.
- Added retry/backoff support to the HTTP client.
- Added reusable response contract assertions.
- Added correlation id echoing and logging in the mock service.
- Added `/metrics` endpoint for runtime observability.
- Hardened REST negative-path validation with stable `errorCode` values.
- Added pytest JSON summary reporting under `reports/test_summary.json`.
- Added GitHub Actions CI workflow and HTML report upload.
- Added `scripts/smoke_check.py` for fast service health checks.
