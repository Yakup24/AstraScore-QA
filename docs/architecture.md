# Architecture

AstraScore QA models the QA side of an enterprise scoring or decision-engine platform. It validates service contracts, scoring outputs, data persistence, regression risk, and report generation using synthetic data.

## High-Level Architecture

```text
User / CI Pipeline
  -> Pytest Runner
  -> Test Data Loader
  -> API Client
  -> Mock or Target Scoring Service
  -> Response Validator
  -> Regression Comparator
  -> Report Writer
  -> JSON / HTML / CI Output
```

## Component Responsibilities

| Component | Responsibility |
| --- | --- |
| Pytest Runner | Discovers and executes smoke, contract, regression, negative, boundary, DB, and report tests. |
| Test Data Loader | Loads synthetic XML, JSON, SQL, and baseline fixtures from `testdata/` and `examples/`. |
| API Client | Sends HTTP requests with timeout and retry/backoff handling. |
| Mock Scoring Service | Provides local SOAP and REST endpoints with deterministic scoring behavior. |
| Response Validator | Checks required fields, score types, decision values, and payload structure. |
| Regression Comparator | Compares actual score and decision outputs with reviewed synthetic baselines. |
| Report Writer | Creates JSON report payloads for audit-friendly test evidence. |

## Test Execution Lifecycle

1. Pytest starts a temporary runtime directory.
2. SQLite demo tables and baseline records are initialized.
3. Mock service starts on a free local port.
4. Tests load synthetic request data.
5. The HTTP client calls the mock SOAP or REST endpoint.
6. Assertions validate HTTP status, response shape, scoring output, DB output, logs, and metrics.
7. Regression tests compare actual score behavior with deterministic baselines.
8. Session hooks write `reports/test_summary.json`.
9. Optional pytest-html output writes `reports/report.html`.

## Data Flow

Real-time flow:

```text
Synthetic SOAP XML
  -> HTTP Client
  -> Mock SOAP Endpoint
  -> Deterministic Score Logic
  -> realtime_results table
  -> SOAP Response
  -> Contract and DB Assertions
```

Batch flow:

```text
Synthetic Batch JSON
  -> HTTP Client
  -> Mock REST Endpoint
  -> Deterministic Score Logic
  -> batch_results table
  -> Batch Result Endpoint
  -> Contract, Count, DB, and Regression Assertions
```

## Error Handling

The mock service returns stable error codes for invalid REST payloads, including:

- `INVALID_JSON`
- `INVALID_PAYLOAD`
- `MISSING_BATCH_ID`
- `INVALID_MODEL_CODE`
- `INVALID_RECORDS`
- `EMPTY_RECORDS`
- `INVALID_RECORD`
- `MISSING_CUSTOMER_ID`
- `INVALID_AMOUNT`

SOAP negative scenarios return SOAP faults with safe XML escaping.

## Mock Service Usage

The mock service is intended for local and CI execution. It avoids real endpoints, real customer data, and external dependencies. It should be replaced or configured through `SCORING_BASE_URL` when testing a controlled integration environment.

## Report Generation Flow

```text
Pytest Result Hook
  -> Test Outcome Collection
  -> Summary Counts
  -> reports/test_summary.json

Standalone Report Writer
  -> ReportCaseResult list
  -> build_report()
  -> write_json_report()
```
