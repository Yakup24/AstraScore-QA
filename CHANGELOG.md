# Changelog

## 2.2.0 - Senior Framework Polish

- Added synthetic request and response validators.
- Added baseline regression comparator with tolerance handling.
- Added standalone JSON report writer.
- Added contract, boundary, regression comparator, report writer, and HTTP resilience tests.
- Added synthetic examples for request, response, baseline, negative, boundary, report, console output, and environment config.
- Added `.env.example`.
- Added senior-level README structure with problem, solution, architecture, design philosophy, usage, limitations, and roadmap.
- Added documentation for test strategy, model regression, data contracts, CI quality gates, security/privacy, and design decisions.
- Added CI workflow with lint, secret inventory, pytest, and report artifact upload.

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
