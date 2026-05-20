from __future__ import annotations

import json
from pathlib import Path

import pytest

from astrascore_qa.validators import (
    ContractValidationError,
    assert_valid_score_request,
    assert_valid_score_response,
    validate_score_request,
    validate_score_response,
)


def _load_json(project_root: Path, relative_path: str) -> dict:
    return json.loads((project_root / relative_path).read_text(encoding="utf-8"))


@pytest.mark.contract
def test_score_request_contract_accepts_synthetic_payload(project_root: Path):
    payload = _load_json(project_root, "examples/sample-score-request.json")

    assert validate_score_request(payload) == []
    assert_valid_score_request(payload)


@pytest.mark.contract
def test_score_response_contract_accepts_required_fields(project_root: Path):
    payload = _load_json(project_root, "examples/sample-score-response.json")

    assert validate_score_response(payload) == []
    assert_valid_score_response(payload)


@pytest.mark.contract
def test_score_response_contract_rejects_invalid_decision(project_root: Path):
    payload = _load_json(project_root, "examples/sample-score-response.json")
    payload["decision"] = "manual_review_required"

    issues = validate_score_response(payload)

    assert [issue.field for issue in issues] == ["decision"]
    with pytest.raises(ContractValidationError, match="decision"):
        assert_valid_score_response(payload)


@pytest.mark.contract
def test_negative_request_collects_all_relevant_contract_issues(project_root: Path):
    payload = _load_json(project_root, "examples/sample-negative-request.json")

    issues = validate_score_request(payload)

    assert {issue.field for issue in issues} == {
        "applicantId",
        "age",
        "monthlyIncome",
        "employmentStatus",
        "requestedAmount",
        "existingDebt",
        "creditHistoryMonths",
    }
