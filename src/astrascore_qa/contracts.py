from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests

CORRELATION_ID_HEADER = "X-Correlation-ID"


def assert_http_status(response: requests.Response, expected_status: int) -> None:
    assert response.status_code == expected_status, (
        f"Expected HTTP {expected_status}, got {response.status_code}. "
        f"Body: {response.text[:500]}"
    )


def json_body(response: requests.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError(f"Response is not valid JSON: {response.text[:500]}") from exc
    assert isinstance(body, dict), f"Expected JSON object, got {type(body).__name__}"
    return body


def assert_required_keys(payload: dict[str, Any], required_keys: Iterable[str], context: str) -> None:
    missing = [key for key in required_keys if key not in payload]
    assert not missing, f"{context} missing required keys: {', '.join(missing)}"


def assert_score_contract(payload: dict[str, Any], accepted_decisions: Iterable[str]) -> None:
    assert_required_keys(payload, ("score", "decision"), "score payload")
    assert isinstance(payload["score"], int), f"score must be int, got {type(payload['score']).__name__}"
    assert 0 <= payload["score"] <= 1000, f"score out of supported range: {payload['score']}"
    assert payload["decision"] in set(accepted_decisions), f"unexpected decision: {payload['decision']}"


def assert_batch_acceptance(payload: dict[str, Any], batch_id: str, total_records: int) -> None:
    assert_required_keys(payload, ("batchId", "status", "totalRecords"), "batch acceptance")
    assert payload["batchId"] == batch_id
    assert payload["status"] == "ACCEPTED"
    assert payload["totalRecords"] == total_records


def assert_batch_results_contract(
    payload: dict[str, Any],
    accepted_decisions: Iterable[str],
    expected_count: int | None = None,
) -> None:
    assert_required_keys(payload, ("batchId", "status", "results"), "batch result")
    assert payload["status"] in {"COMPLETED", "NOT_FOUND"}
    assert isinstance(payload["results"], list), "batch result results must be a list"
    if expected_count is not None:
        assert len(payload["results"]) == expected_count
    for row in payload["results"]:
        assert isinstance(row, dict), f"batch result row must be an object: {row!r}"
        assert_score_contract(row, accepted_decisions)


def assert_correlation_id(response: requests.Response, expected_correlation_id: str) -> None:
    assert response.headers.get(CORRELATION_ID_HEADER) == expected_correlation_id
