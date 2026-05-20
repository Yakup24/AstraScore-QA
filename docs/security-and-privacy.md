# Security and Privacy

## Synthetic Data Policy

This repository must only use synthetic demo data. Do not commit real customer records, real financial decisions, national IDs, account numbers, phone numbers, emails, addresses, access tokens, certificates, or internal service URLs.

## Secret Management

Secrets must be provided through:

- environment variables
- GitHub Actions secrets
- local files excluded by `.gitignore`
- an approved vault in real environments

Do not store credentials in `config/config.yaml`, examples, tests, logs, or documentation.

## Log Masking

Current demo logs contain synthetic transaction and customer identifiers only. Real integrations should mask or omit:

- customer identifiers
- account numbers
- national identifiers
- raw request bodies
- tokens and credentials

## Test Data Storage

Local SQLite data, logs, generated reports, caches, and virtual environments are ignored by git. Test data committed to the repository should remain synthetic and reviewable.

## Environment Variable Usage

Supported environment overrides:

```text
SCORING_BASE_URL
SCORING_DB_PATH
SCORING_LOG_FILE
SCORING_MODEL_CODE
SCORING_CONNECT_TIMEOUT
SCORING_READ_TIMEOUT
```

## Production Endpoint Warning

This repository is not prepared to run directly against production scoring systems. Real environments require authorization, isolated test data, network controls, audit approval, and model governance review.

## Responsible Testing

This repo is for QA automation and demonstration. Before institutional use, it should pass internal security, privacy, compliance, and model governance processes.
