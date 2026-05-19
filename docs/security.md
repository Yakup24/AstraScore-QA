# AstraScore QA Security Notes

## Security Controls

AstraScore QA includes repository-level controls and CI checks for common open-source and enterprise risks:

- CodeQL for semantic code scanning
- Bandit for Python security linting
- pip-audit for dependency CVE checks
- Gitleaks for secret scanning
- Dependabot for dependency and GitHub Actions updates
- CODEOWNERS for review ownership
- MIT license clarity
- Private vulnerability reporting guidance

## Data Safety

The mock service uses deterministic demo scoring data only. Do not add real customer identifiers, account numbers, national ids, production MSISDN values, or bank-internal endpoint details to `testdata/`.

## Configuration Safety

Use environment variables for environment-specific overrides:

```text
SCORING_BASE_URL
SCORING_DB_PATH
SCORING_LOG_FILE
SCORING_MODEL_CODE
SCORING_CONNECT_TIMEOUT
SCORING_READ_TIMEOUT
```

Production credentials should be injected through CI secrets or a secure vault. They should never be stored in `config/config.yaml`.

## CI Security Gates

The `Security` workflow runs on push, pull request, weekly schedule, and manual dispatch. It fails the build when high-confidence secret leaks or security scan failures are detected.

## Local Security Commands

```bash
python -m pip install -r requirements-dev.txt
ruff check .
bandit -c pyproject.toml -r src mock_service scripts
pip-audit -r requirements.txt
detect-secrets scan --all-files --exclude-files '(^\.git[\\/]|^\.venv[\\/]|^\.ruff_cache[\\/]|^\.pytest_cache[\\/]|^reports[\\/]|^data[\\/]|^logs[\\/])'
```
