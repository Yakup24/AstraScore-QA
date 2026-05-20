from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BaselineFormatError(ValueError):
    """Raised when a regression baseline file cannot be used safely."""


@dataclass(frozen=True)
class BaselineCase:
    case_id: str
    expected_score: int
    tolerance: int
    expected_decision: str


@dataclass(frozen=True)
class RegressionComparison:
    case_id: str
    expected_score: int
    actual_score: int
    tolerance: int
    expected_decision: str
    actual_decision: str

    @property
    def score_delta(self) -> int:
        return self.actual_score - self.expected_score

    @property
    def passed(self) -> bool:
        return abs(self.score_delta) <= self.tolerance and self.actual_decision == self.expected_decision

    @property
    def reason(self) -> str | None:
        if abs(self.score_delta) > self.tolerance:
            return "actual score exceeded allowed tolerance"
        if self.actual_decision != self.expected_decision:
            return "actual decision changed from baseline"
        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "caseId": self.case_id,
            "expectedScore": self.expected_score,
            "actualScore": self.actual_score,
            "scoreDelta": self.score_delta,
            "tolerance": self.tolerance,
            "expectedDecision": self.expected_decision,
            "actualDecision": self.actual_decision,
            "passed": self.passed,
            "reason": self.reason,
        }


def load_regression_baseline(path: str | Path) -> list[BaselineCase]:
    """Load a synthetic regression baseline from JSON."""
    baseline_path = Path(path)
    try:
        payload = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BaselineFormatError(f"Baseline file is not valid JSON: {baseline_path}") from exc

    if not isinstance(payload, dict):
        raise BaselineFormatError("Baseline root must be a JSON object")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise BaselineFormatError("Baseline must contain a non-empty cases list")

    return [_parse_case(case, index) for index, case in enumerate(cases)]


def compare_to_baseline(
    baseline_case: BaselineCase,
    actual_score: int,
    actual_decision: str,
) -> RegressionComparison:
    return RegressionComparison(
        case_id=baseline_case.case_id,
        expected_score=baseline_case.expected_score,
        actual_score=actual_score,
        tolerance=baseline_case.tolerance,
        expected_decision=baseline_case.expected_decision,
        actual_decision=actual_decision,
    )


def compare_many(
    baseline_cases: list[BaselineCase],
    actual_results: dict[str, dict[str, Any]],
) -> list[RegressionComparison]:
    comparisons: list[RegressionComparison] = []
    for baseline_case in baseline_cases:
        actual = actual_results.get(baseline_case.case_id)
        if actual is None:
            raise BaselineFormatError(f"Missing actual result for baseline case: {baseline_case.case_id}")
        comparisons.append(
            compare_to_baseline(
                baseline_case,
                actual_score=_required_int(actual, "score", baseline_case.case_id),
                actual_decision=_required_str(actual, "decision", baseline_case.case_id),
            )
        )
    return comparisons


def _parse_case(case: Any, index: int) -> BaselineCase:
    if not isinstance(case, dict):
        raise BaselineFormatError(f"Baseline case at index {index} must be an object")
    case_id = _required_str(case, "caseId", f"index {index}")
    expected_score = _required_int(case, "expectedScore", case_id)
    tolerance = _required_int(case, "tolerance", case_id)
    expected_decision = _required_str(case, "expectedDecision", case_id)
    if tolerance < 0:
        raise BaselineFormatError(f"Baseline case {case_id} has negative tolerance")
    return BaselineCase(
        case_id=case_id,
        expected_score=expected_score,
        tolerance=tolerance,
        expected_decision=expected_decision,
    )


def _required_int(payload: dict[str, Any], key: str, context: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise BaselineFormatError(f"{context}: {key} must be an integer")
    return value


def _required_str(payload: dict[str, Any], key: str, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BaselineFormatError(f"{context}: {key} must be a non-empty string")
    return value
