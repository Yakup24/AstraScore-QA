from __future__ import annotations

import json

import pytest

from astrascore_qa.regression import (
    BaselineCase,
    BaselineFormatError,
    compare_many,
    compare_to_baseline,
    load_regression_baseline,
)


@pytest.mark.regression
def test_regression_score_within_tolerance_should_pass():
    baseline = BaselineCase(
        case_id="baseline-low-risk-001",
        expected_score=742,
        tolerance=5,
        expected_decision="approved",
    )

    result = compare_to_baseline(baseline, actual_score=745, actual_decision="approved")

    assert result.passed
    assert result.score_delta == 3
    assert result.reason is None


@pytest.mark.regression
def test_regression_score_outside_tolerance_should_fail():
    baseline = BaselineCase(
        case_id="baseline-high-risk-001",
        expected_score=518,
        tolerance=5,
        expected_decision="review",
    )

    result = compare_to_baseline(baseline, actual_score=531, actual_decision="review")

    assert not result.passed
    assert result.reason == "actual score exceeded allowed tolerance"


@pytest.mark.regression
def test_regression_decision_change_should_fail():
    baseline = BaselineCase(
        case_id="baseline-low-risk-001",
        expected_score=742,
        tolerance=5,
        expected_decision="approved",
    )

    result = compare_to_baseline(baseline, actual_score=742, actual_decision="review")

    assert not result.passed
    assert result.reason == "actual decision changed from baseline"


@pytest.mark.regression
def test_regression_baseline_loader_rejects_broken_baseline(tmp_path):
    baseline_path = tmp_path / "broken-baseline.json"
    baseline_path.write_text(json.dumps({"cases": [{"caseId": "missing-score"}]}), encoding="utf-8")

    with pytest.raises(BaselineFormatError, match="expectedScore"):
        load_regression_baseline(baseline_path)


@pytest.mark.regression
def test_regression_compare_many_uses_baseline_file(project_root):
    baseline_cases = load_regression_baseline(project_root / "examples/sample-regression-baseline.json")
    actual_results = {
        "baseline-low-risk-001": {"score": 743, "decision": "approved"},
        "baseline-high-risk-001": {"score": 517, "decision": "review"},
    }

    comparisons = compare_many(baseline_cases, actual_results)

    assert len(comparisons) == 2
    assert all(comparison.passed for comparison in comparisons)
