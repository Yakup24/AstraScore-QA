# Design Decisions

## Why Python?

Python is a practical choice for scoring QA because the same project often touches API testing, data checks, model regression, JSON/XML parsing, reporting, and CI automation. Python also fits teams that already use notebooks, model validation scripts, or data engineering utilities.

Trade-off: Python is not the only valid option. Java, TypeScript, Robot Framework, and Postman/Newman can all be appropriate depending on team stack and governance requirements.

## Why pytest?

pytest provides simple tests, fixtures, markers, parametrization, and CI-friendly output. The current suite uses markers for smoke, contract, regression, negative, boundary, report, and performance-style checks.

Trade-off: pytest requires discipline around fixture design and test naming as suites grow.

## Why Synthetic Data?

Synthetic data keeps the repository safe for public sharing and avoids dependency on regulated customer records. It also makes tests deterministic and reviewable.

Trade-off: synthetic data cannot fully represent real portfolio behavior. Production use requires controlled, approved test data.

## Why Baseline Regression?

Scoring systems need stable reference cases. Baseline regression helps detect unintended changes in score and decision output after code or model updates.

Trade-off: baselines can become stale. Updates should be reviewed by model and business stakeholders.

## Why a Mock Scoring Service?

The mock service lets the framework run locally and in CI without network dependencies or real endpoints. It proves test orchestration, assertion logic, logging, metrics, and database validation.

Trade-off: a mock service does not prove that a real integration environment behaves the same way.

## Why CI Quality Gates?

CI gates make quality visible before merge. This repository includes lint, tests, dependency audit, static security scan, secret scanning, and CodeQL.

Trade-off: security gates can need tuning to reduce false positives.

## Alternatives

| Alternative | Strength | Trade-off |
| --- | --- | --- |
| Postman/Newman | Strong API collection workflow | Weaker for DB checks and custom regression logic. |
| Robot Framework | Readable keyword-driven tests | Can become verbose for Python-native validation logic. |
| Custom shell scripts | Simple for smoke checks | Harder to maintain and scale. |
| Manual QA | Useful for exploratory checks | Not reliable for repeatable CI regression coverage. |
| Java/TypeScript framework | Strong enterprise stack alignment | More setup for data/model validation workflows. |

## Current Decision

AstraScore QA keeps the framework Python-based and pytest-driven because it balances API testing, data validation, regression comparison, security tooling, and report generation in a compact repository.
