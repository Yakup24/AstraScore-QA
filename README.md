# AstraScore QA

[![Enterprise Scoring Tests](https://github.com/Yakup24/AstraScore-QA/actions/workflows/tests.yml/badge.svg)](https://github.com/Yakup24/AstraScore-QA/actions/workflows/tests.yml)
[![Security](https://github.com/Yakup24/AstraScore-QA/actions/workflows/security.yml/badge.svg)](https://github.com/Yakup24/AstraScore-QA/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AstraScore QA is an enterprise-style Python test automation framework for validating real-time and batch scoring platforms. It covers SOAP, REST, database output, model regression, negative scenarios, concurrency smoke checks, observability, and CI security gates with a local mock scoring service.

The project is designed for banking, credit-risk, telecom, and large-scale decisioning systems where score outputs must be validated across API, data, and operational layers.

## Capabilities

- SOAP real-time scoring validation
- REST batch scoring submission and result polling
- SQLite demo output validation with a replaceable DB adapter boundary
- Model baseline regression checks
- Negative-path API contract checks with stable error codes
- Correlation id echo and log traceability
- `/metrics` endpoint for mock runtime counters
- Retry/backoff enabled HTTP client
- JSON and HTML pytest reporting
- GitHub Actions test workflow
- CodeQL, Bandit, pip-audit, Gitleaks, and Dependabot security coverage

## Project Layout

```text
AstraScore-QA/
├── .github/
│   ├── workflows/
│   │   ├── security.yml
│   │   └── tests.yml
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── config/
│   └── config.yaml
├── docs/
│   ├── architecture.md
│   ├── operations.md
│   └── security.md
├── mock_service/
│   └── server.py
├── scripts/
│   ├── init_db.py
│   └── smoke_check.py
├── src/
│   └── astrascore_qa/
├── testdata/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── SECURITY.md
├── pyproject.toml
├── requirements-dev.txt
└── requirements.txt
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest
```

For HTML and JSON reports:

```bash
python -m pytest --html=reports/report.html --self-contained-html
```

Generated reports:

- `reports/report.html`
- `reports/test_summary.json`

## Mock Service

Run the local scoring mock manually:

```bash
python scripts/init_db.py
python -m mock_service.server
```

Available endpoints:

```text
GET  http://127.0.0.1:8089/health
GET  http://127.0.0.1:8089/metrics
POST http://127.0.0.1:8089/soap/realtime-scoring
POST http://127.0.0.1:8089/api/v1/batch-scoring
GET  http://127.0.0.1:8089/api/v1/batch-scoring/{batchId}
```

## Smoke Check

With the mock service running:

```bash
python scripts/smoke_check.py
```

The script verifies health status and correlation id propagation.

## Configuration

Runtime settings live in `config/config.yaml`.

Environment overrides:

```text
SCORING_BASE_URL
SCORING_DB_PATH
SCORING_LOG_FILE
SCORING_MODEL_CODE
SCORING_CONNECT_TIMEOUT
SCORING_READ_TIMEOUT
```

The config loader validates required service paths, timeout values, database settings, model decisions, observability settings, and retry settings before tests run.

## Security

AstraScore QA ships with a DevSecOps baseline:

- `SECURITY.md` vulnerability reporting policy
- CodeQL static analysis workflow
- Bandit Python security scan
- pip-audit dependency vulnerability scan
- Gitleaks secret scanning
- Dependabot for Python packages and GitHub Actions
- CODEOWNERS and PR template
- `.gitignore` rules for local DBs, logs, venvs, caches, and generated reports

See `docs/security.md` for details.

## CI

GitHub Actions workflows:

- `.github/workflows/tests.yml`: lint, tests, HTML report artifact
- `.github/workflows/security.yml`: CodeQL, secret scan, dependency audit, Bandit

## Real Environment Adaptation

For real scoring environments, usually only these layers change:

- `config/config.yaml` for service URLs and paths
- `src/astrascore_qa/db.py` for Oracle, Exadata, PostgreSQL, SQL Server, Hive, Impala, or DWH adapters
- `testdata/` for institution-specific SOAP, REST, and SQL contracts
- CI secrets and environment variables for protected integration targets

## License

MIT License. See `LICENSE`.
