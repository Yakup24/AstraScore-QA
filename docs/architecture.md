# Architecture

AstraScore QA models the QA side of an enterprise scoring landscape.

## Logical Flow

```text
Business App / Channel
  -> SOAP real-time scoring
  -> REST batch scoring
  -> Score output persistence
  -> Database and model baseline validation
  -> Reports and CI evidence
```

## Demo Mapping

| Enterprise Component | AstraScore QA Demo |
| --- | --- |
| Scoring Proxy / SOAP | `/soap/realtime-scoring` |
| Batch Scoring API | `/api/v1/batch-scoring` |
| DWH / Exadata output | SQLite `realtime_results` and `batch_results` |
| Model Repository | SQLite `model_baseline` |
| Observability | correlation id, log file, `/metrics` |
| Test Automation | pytest suite |
| CI Evidence | HTML report, JSON summary, Actions artifacts |

## Core Modules

- `src/astrascore_qa/config.py`: config loading, environment overrides, validation
- `src/astrascore_qa/http_client.py`: retry/backoff HTTP client
- `src/astrascore_qa/contracts.py`: reusable response contract assertions
- `src/astrascore_qa/db.py`: replaceable SQLite demo adapter
- `src/astrascore_qa/soap.py`: SOAP rendering and parsing helpers
- `mock_service/server.py`: local scoring mock service

## Production Adaptation Points

1. Replace mock endpoints with integration environment URLs.
2. Replace SQLite with the target RDBMS, DWH, or query layer adapter.
3. Version model baselines as reviewed test assets.
4. Inject secrets through CI secrets or a vault.
5. Keep test reports as audit artifacts.

## Suggested Pipeline

```text
Commit
  -> Ruff lint
  -> Unit and integration-style mock tests
  -> CodeQL
  -> Bandit
  -> pip-audit
  -> Gitleaks
  -> HTML and JSON reports
  -> Artifact retention
```
