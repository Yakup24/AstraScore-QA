# Test Strategy

## Testing Goals

- Keep API request and response contracts stable.
- Detect unintended scoring output changes.
- Validate negative and boundary behavior.
- Verify database output consistency.
- Keep checks fast enough for CI quality gates.
- Use only synthetic, repeatable fixtures.

## Test Types

| Type | Purpose |
| --- | --- |
| Contract tests | Validate required fields, enum values, numeric score ranges, and response shape. |
| Regression tests | Compare actual score and decision outputs against synthetic baselines. |
| Negative tests | Exercise invalid payloads, malformed JSON, missing fields, and invalid numeric values. |
| Boundary tests | Check edge cases such as minimum age, maximum age, zero debt, and positive amount rules. |
| Smoke tests | Verify health, metrics, correlation id, retry, timeout, and basic concurrency behavior. |
| Mock service tests | Validate local SOAP and REST mock behavior without external dependencies. |
| Data validation tests | Compare service outputs with records persisted into the demo database. |
| Report tests | Ensure JSON report generation works for failed and empty suites. |

## Test Data Strategy

- All fixtures are synthetic.
- No real customer data is allowed.
- Examples are deterministic and safe for public repositories.
- Regression baselines should be reviewed before being treated as a quality gate.
- Baseline changes should be intentional and visible in pull requests.

## What Should Not Be Tested Directly

- Real production customer data.
- Uncontrolled live endpoints.
- Real financial decisions without business and model governance approval.
- Production credentials or internal service URLs in repository files.

## CI Test Strategy

- Fast tests run on every push and pull request.
- Regression tests run as part of the default pytest suite.
- Security checks run in a separate workflow and on a weekly schedule.
- Extended performance and drift checks are planned for future releases.
