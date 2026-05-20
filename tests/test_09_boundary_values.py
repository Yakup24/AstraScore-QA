from __future__ import annotations

import json
from pathlib import Path

import pytest

from astrascore_qa.validators import validate_score_request


def _base_payload(project_root: Path) -> dict:
    return json.loads((project_root / "examples/sample-score-request.json").read_text(encoding="utf-8"))


@pytest.mark.boundary
@pytest.mark.parametrize("age", [18, 75])
def test_age_boundaries_are_accepted(project_root: Path, age: int):
    payload = _base_payload(project_root)
    payload["age"] = age

    assert validate_score_request(payload) == []


@pytest.mark.boundary
@pytest.mark.parametrize("age", [17, 76])
def test_age_outside_supported_boundary_is_rejected(project_root: Path, age: int):
    payload = _base_payload(project_root)
    payload["age"] = age

    issues = validate_score_request(payload)

    assert [issue.field for issue in issues] == ["age"]


@pytest.mark.boundary
def test_zero_existing_debt_is_accepted(project_root: Path):
    payload = _base_payload(project_root)
    payload["existingDebt"] = 0

    assert validate_score_request(payload) == []


@pytest.mark.boundary
def test_requested_amount_must_be_positive(project_root: Path):
    payload = _base_payload(project_root)
    payload["requestedAmount"] = 0

    issues = validate_score_request(payload)

    assert [issue.field for issue in issues] == ["requestedAmount"]


@pytest.mark.boundary
def test_low_income_high_debt_payload_remains_schema_valid(project_root: Path):
    payload = _base_payload(project_root)
    payload["monthlyIncome"] = 0
    payload["existingDebt"] = 250000
    payload["requestedAmount"] = 500000

    assert validate_score_request(payload) == []
