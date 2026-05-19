# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| 2.x | Yes |
| < 2.0 | No |

## Reporting a Vulnerability

Please report vulnerabilities through GitHub private vulnerability reporting:

https://github.com/Yakup24/AstraScore-QA/security/advisories/new

Do not create a public issue for secrets, credential exposure, injection risks, or vulnerabilities that could affect real scoring environments.

## Expected Response

- Initial review target: 72 hours
- Fix or mitigation target: depends on severity and exploitability
- Public disclosure: after a fix or mitigation is available

## Security Baseline

This repository enables a defensive baseline through:

- CodeQL analysis
- Bandit static Python scan
- pip-audit dependency scan
- Gitleaks secret scanning
- Dependabot updates
- CODEOWNERS review ownership
- Generated DB, report, cache, venv, and log exclusions

## Handling Secrets

Never commit:

- API keys
- database credentials
- bank/customer data
- production endpoints that are not intended to be public
- private certificates
- `.env` files

Use GitHub Actions secrets for CI-only credentials.
