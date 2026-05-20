# CI Quality Gates

This repository includes implemented gates and recommended gates for future production usage.

## Implemented Gates

- Pytest suite must pass.
- Ruff lint must pass.
- Bandit security scan must pass.
- pip-audit must report no known vulnerabilities in pinned dependencies.
- detect-secrets inventory should return no findings for repository files.
- Gitleaks runs in GitHub Actions.
- CodeQL runs in GitHub Actions.
- Generated reports are uploaded as CI artifacts.

## Recommended Quality Gates

For a production scoring program, teams should also consider:

1. Unit tests must pass.
2. Contract tests must pass.
3. Regression tests must not exceed tolerance.
4. No hardcoded secrets.
5. No real customer data in fixtures.
6. Lint checks must pass.
7. Pull requests should include test evidence.
8. Baseline changes should require reviewer approval.
9. Performance thresholds should be tracked over time.
10. Data drift and decision distribution should be reviewed.

## Pull Request Expectations

Each pull request should describe:

- changed behavior
- affected test categories
- validation commands
- regression or baseline impact
- security and privacy impact

## Failure Policy

A failed quality gate should block merge until it is understood. For model regression failures, the fix may be either code correction or a reviewed baseline update.
