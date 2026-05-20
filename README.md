# AstraScore QA

[![CI](https://github.com/Yakup24/AstraScore-QA/actions/workflows/ci.yml/badge.svg)](https://github.com/Yakup24/AstraScore-QA/actions/workflows/ci.yml)
[![Enterprise Scoring Tests](https://github.com/Yakup24/AstraScore-QA/actions/workflows/tests.yml/badge.svg)](https://github.com/Yakup24/AstraScore-QA/actions/workflows/tests.yml)
[![Security](https://github.com/Yakup24/AstraScore-QA/actions/workflows/security.yml/badge.svg)](https://github.com/Yakup24/AstraScore-QA/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AstraScore QA is a Python-based QA automation framework for scoring, risk, and decision-engine platforms. It validates API contracts, synthetic model outputs, regression baselines, negative scenarios, boundary values, observability signals, and CI quality gates.

The goal is not to claim a production scoring model. The goal is to show how a scoring platform can be tested with deterministic, privacy-safe, CI-ready automation.

## Overview

Scoring systems often sit between business channels, model logic, data platforms, and downstream decision workflows. A small service, data, or model change can alter approval decisions, break API contracts, or create incorrect output records.

AstraScore QA provides a working reference framework for validating those risks with:

- deterministic synthetic input data
- mock scoring endpoints for local execution
- SOAP and REST test coverage
- reusable contract validators
- regression baseline comparison with tolerance
- JSON and HTML report generation
- security and privacy guardrails
- GitHub Actions quality gates

The project can be used by QA automation engineers, backend developers, data engineers, model validation teams, and technical reviewers who need a realistic scoring QA example.

## Problem

Scoring and decision systems are risky to test manually because:

- small code or model changes can shift score and decision outputs
- API contract changes can break downstream systems
- batch outputs can disagree with service responses or database records
- negative and boundary cases are easy to miss
- real customer data is unsafe for public or portfolio repositories
- manual regression testing does not scale in CI/CD

## Solution

AstraScore QA addresses those risks through:

- synthetic-only test fixtures
- API contract tests for required request and response fields
- deterministic baseline checks for model regression
- negative scenario tests for invalid payloads
- boundary value tests for edge inputs
- concurrent smoke tests for basic service stability
- report writer tests for audit-friendly JSON output
- CI workflows for lint, tests, dependency audit, static scan, and secret scan

## Architecture

```text
User or CI Pipeline
  -> Pytest Runner
  -> Test Data Loader
  -> API Client
  -> Mock or Target Scoring Endpoint
  -> Assertion and Contract Layer
  -> Regression Comparator
  -> Report Writer
  -> JSON / HTML / CI Output
```

Core components:

- `src/astrascore_qa/http_client.py`: retry/backoff HTTP client
- `src/astrascore_qa/validators.py`: synthetic request and response contract validators
- `src/astrascore_qa/regression.py`: baseline loader and tolerance comparator
- `src/astrascore_qa/report.py`: JSON report builder and writer
- `src/astrascore_qa/contracts.py`: reusable HTTP/API assertion helpers
- `mock_service/server.py`: local SOAP/REST scoring mock
- `tests/`: pytest suite covering service, data, model, boundary, reporting, and resilience paths

## Design Philosophy

AstraScore QA is built around three principles:

1. Deterministic validation  
   Scoring outputs should be validated against stable synthetic baselines to detect unintended regressions.

2. Contract safety  
   API request and response structures should remain predictable for downstream systems.

3. Privacy-first testing  
   Test automation must not depend on real customer data. All sample fixtures are synthetic and safe for public repositories.

## Why Python?

Python is used deliberately because scoring QA sits close to API testing, data validation, model regression, and reporting. Python gives strong library support for pytest, HTTP clients, JSON/XML processing, data fixtures, CI execution, and future analytical extensions. A Java, TypeScript, Postman/Newman, or Robot Framework version could also work, but Python is a practical fit for teams that need one language across QA, backend validation, and data/model testing.

## Core Features

- API contract testing
- Synthetic request and response validation
- Model regression baseline comparison
- Tolerance-based regression checks
- Negative test scenarios
- Boundary value tests
- SOAP real-time scoring mock tests
- REST batch scoring mock tests
- Database output validation
- Concurrent smoke tests
- Retry/timeout client resilience tests
- JSON report output
- HTML pytest report output
- CI-friendly pytest execution
- DevSecOps baseline with CodeQL, Bandit, pip-audit, Gitleaks, detect-secrets, and Dependabot

## Tech Stack

- Python 3.10+
- pytest
- requests
- PyYAML
- defusedxml
- SQLite for demo persistence
- pytest-html for HTML reporting
- Ruff for linting
- Bandit and pip-audit for security checks
- GitHub Actions for CI/CD

FastAPI and pydantic are not used in this repository. The mock service is built with Python's standard HTTP server to keep the demo lightweight and dependency-minimal.

## Project Structure

```text
AstraScore-QA/
|-- .github/
|   |-- workflows/
|   |   |-- ci.yml
|   |   |-- security.yml
|   |   `-- tests.yml
|   |-- dependabot.yml
|   |-- CODEOWNERS
|   |-- ISSUE_TEMPLATE/
|   `-- pull_request_template.md
|-- config/
|   `-- config.yaml
|-- docs/
|   |-- architecture.md
|   |-- ci-quality-gates.md
|   |-- data-contracts.md
|   |-- design-decisions.md
|   |-- model-regression.md
|   |-- operations.md
|   |-- security-and-privacy.md
|   |-- security.md
|   `-- test-strategy.md
|-- examples/
|   |-- sample-score-request.json
|   |-- sample-score-response.json
|   |-- sample-regression-baseline.json
|   |-- sample-negative-request.json
|   |-- sample-boundary-request.json
|   |-- sample-test-report.json
|   |-- sample-console-output.txt
|   `-- config.example.env
|-- mock_service/
|   `-- server.py
|-- scripts/
|   |-- init_db.py
|   `-- smoke_check.py
|-- src/
|   `-- astrascore_qa/
|       |-- config.py
|       |-- contracts.py
|       |-- db.py
|       |-- http_client.py
|       |-- log_checker.py
|       |-- regression.py
|       |-- report.py
|       |-- soap.py
|       `-- validators.py
|-- testdata/
|-- tests/
|-- .env.example
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- pyproject.toml
|-- requirements-dev.txt
|-- requirements.txt
`-- SECURITY.md
```

## Getting Started

```bash
git clone https://github.com/Yakup24/AstraScore-QA.git
cd AstraScore-QA
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
```

Run the mock service manually:

```bash
python scripts/init_db.py
python -m mock_service.server
```

Mock endpoints:

```text
GET  http://127.0.0.1:8089/health
GET  http://127.0.0.1:8089/metrics
POST http://127.0.0.1:8089/soap/realtime-scoring
POST http://127.0.0.1:8089/api/v1/batch-scoring
GET  http://127.0.0.1:8089/api/v1/batch-scoring/{batchId}
```

## Configuration

Runtime settings live in `config/config.yaml`.

Environment examples are provided in:

- `.env.example`
- `examples/config.example.env`

Supported overrides:

```text
SCORING_BASE_URL
SCORING_DB_PATH
SCORING_LOG_FILE
SCORING_MODEL_CODE
SCORING_CONNECT_TIMEOUT
SCORING_READ_TIMEOUT
TEST_ENV
REPORT_PATH
```

Use placeholders or local mock URLs in public repositories. Do not commit real internal endpoints or credentials.

## Usage

Run the full suite:

```bash
python -m pytest
```

Run selected test types:

```bash
python -m pytest -m contract
python -m pytest -m regression
python -m pytest -m negative
python -m pytest -m boundary
python -m pytest -m smoke
```

Generate HTML and JSON reports:

```bash
python -m pytest --html=reports/report.html --self-contained-html
```

Run lint and security checks:

```bash
ruff check .
bandit -c pyproject.toml -r src mock_service scripts
pip-audit -r requirements.txt
detect-secrets scan --all-files --exclude-files '(^\.git[\\/]|^\.venv[\\/]|^\.ruff_cache[\\/]|^\.pytest_cache[\\/]|^reports[\\/]|^data[\\/]|^logs[\\/])'
```

## Test Strategy

Current test coverage includes:

- Contract tests: required fields, enum values, numeric score checks, reason code structure
- Regression tests: expected score, actual score, tolerance, expected decision
- Negative tests: malformed JSON, empty records, missing transaction id, invalid amounts
- Boundary tests: minimum and maximum applicant age, zero debt, positive requested amount
- Smoke tests: health, metrics, correlation id, concurrent real-time scoring
- Mock service tests: SOAP and REST behavior against local deterministic service
- Data validation tests: API/database output consistency
- Report tests: JSON report generation, failure inclusion, empty result handling
- Resilience tests: retry on transient HTTP 500 and controlled timeout failure

## Reporting

The project generates:

- console output from pytest
- `reports/test_summary.json` via pytest session hook
- `reports/report.html` when pytest-html is enabled

`src/astrascore_qa/report.py` also provides a standalone JSON report writer for synthetic suite results.

## Security and Privacy

- All examples are synthetic.
- No real customer data is required.
- No real national IDs, phone numbers, emails, addresses, tokens, or credentials should be committed.
- Secrets should be passed through environment variables, CI secrets, or local ignored files.
- Logs should avoid sensitive values.
- Production scoring endpoints should only be tested with explicit authorization and isolated test data.

## Limitations

- Demo scoring rules do not represent real financial models.
- Regression baselines must be reviewed before production use.
- Real scoring services require controlled test environments and approved test data.
- This project does not replace model governance, explainability review, or business validation.
- OpenAPI schema validation and a drift dashboard are planned, not implemented.

## Roadmap

- OpenAPI schema validation for REST endpoints
- Docker Compose demo environment
- Performance threshold reporting
- Drift detection summary for score and decision distribution
- Coverage badge and coverage threshold gate
- Optional JUnit/XML report publishing

## My Contributions

This repository includes:

- package structure for `astrascore_qa`
- deterministic SOAP and REST mock scoring service
- retry/backoff HTTP client
- config loading and validation
- reusable API contract assertions
- synthetic request/response validators
- baseline regression comparator
- JSON report writer
- SQLite demo output validation
- pytest suite for contract, regression, negative, boundary, smoke, DB, reporting, and resilience checks
- CI and security workflows
- MIT license and GitHub quality files
- technical documentation and synthetic examples

## License

MIT License. See `LICENSE`.
