from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any

SUPPORTED_DECISIONS = {"approved", "review", "rejected"}
SUPPORTED_EMPLOYMENT_STATUSES = {
    "full_time",
    "part_time",
    "self_employed",
    "retired",
    "student",
    "unemployed",
}
SUPPORTED_RISK_BANDS = {"low", "medium", "high"}
MIN_APPLICANT_AGE = 18
MAX_APPLICANT_AGE = 75


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"field": self.field, "message": self.message}


class ContractValidationError(ValueError):
    """Raised when a synthetic scoring contract payload is invalid."""

    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        super().__init__(format_issues(issues))


def validate_score_request(payload: dict[str, Any]) -> list[ValidationIssue]:
    """Validate a synthetic scoring request schema used by examples and tests."""
    issues: list[ValidationIssue] = []

    applicant_id = payload.get("applicantId")
    if not isinstance(applicant_id, str) or not applicant_id.strip():
        issues.append(ValidationIssue("applicantId", "must be a non-empty string"))

    age = payload.get("age")
    if not isinstance(age, int):
        issues.append(ValidationIssue("age", "must be an integer"))
    elif not MIN_APPLICANT_AGE <= age <= MAX_APPLICANT_AGE:
        issues.append(ValidationIssue("age", f"must be between {MIN_APPLICANT_AGE} and {MAX_APPLICANT_AGE}"))

    monthly_income = payload.get("monthlyIncome")
    if not _is_number(monthly_income):
        issues.append(ValidationIssue("monthlyIncome", "must be numeric"))
    elif monthly_income < 0:
        issues.append(ValidationIssue("monthlyIncome", "must be zero or greater"))

    employment_status = payload.get("employmentStatus")
    if employment_status not in SUPPORTED_EMPLOYMENT_STATUSES:
        issues.append(
            ValidationIssue(
                "employmentStatus",
                f"must be one of {', '.join(sorted(SUPPORTED_EMPLOYMENT_STATUSES))}",
            )
        )

    requested_amount = payload.get("requestedAmount")
    if not _is_number(requested_amount):
        issues.append(ValidationIssue("requestedAmount", "must be numeric"))
    elif requested_amount <= 0:
        issues.append(ValidationIssue("requestedAmount", "must be greater than zero"))

    existing_debt = payload.get("existingDebt")
    if not _is_number(existing_debt):
        issues.append(ValidationIssue("existingDebt", "must be numeric"))
    elif existing_debt < 0:
        issues.append(ValidationIssue("existingDebt", "must be zero or greater"))

    credit_history_months = payload.get("creditHistoryMonths")
    if not isinstance(credit_history_months, int):
        issues.append(ValidationIssue("creditHistoryMonths", "must be an integer"))
    elif credit_history_months < 0:
        issues.append(ValidationIssue("creditHistoryMonths", "must be zero or greater"))

    return issues


def validate_score_response(payload: dict[str, Any]) -> list[ValidationIssue]:
    """Validate a synthetic score response schema used by downstream contract tests."""
    issues: list[ValidationIssue] = []

    applicant_id = payload.get("applicantId")
    if not isinstance(applicant_id, str) or not applicant_id.strip():
        issues.append(ValidationIssue("applicantId", "must be a non-empty string"))

    score = payload.get("score")
    if not isinstance(score, int):
        issues.append(ValidationIssue("score", "must be an integer"))
    elif not 0 <= score <= 1000:
        issues.append(ValidationIssue("score", "must be between 0 and 1000"))

    decision = payload.get("decision")
    if decision not in SUPPORTED_DECISIONS:
        issues.append(ValidationIssue("decision", f"must be one of {', '.join(sorted(SUPPORTED_DECISIONS))}"))

    risk_band = payload.get("riskBand")
    if risk_band not in SUPPORTED_RISK_BANDS:
        issues.append(ValidationIssue("riskBand", f"must be one of {', '.join(sorted(SUPPORTED_RISK_BANDS))}"))

    reason_codes = payload.get("reasonCodes")
    if not isinstance(reason_codes, list):
        issues.append(ValidationIssue("reasonCodes", "must be a list"))
    elif not all(isinstance(reason_code, str) and reason_code.strip() for reason_code in reason_codes):
        issues.append(ValidationIssue("reasonCodes", "must contain only non-empty strings"))

    return issues


def assert_valid_score_request(payload: dict[str, Any]) -> None:
    issues = validate_score_request(payload)
    if issues:
        raise ContractValidationError(issues)


def assert_valid_score_response(payload: dict[str, Any]) -> None:
    issues = validate_score_response(payload)
    if issues:
        raise ContractValidationError(issues)


def format_issues(issues: list[ValidationIssue]) -> str:
    return "; ".join(f"{issue.field}: {issue.message}" for issue in issues)


def _is_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)
