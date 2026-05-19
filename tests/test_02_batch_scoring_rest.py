from __future__ import annotations

import pytest

from astrascore_qa.contracts import (
    assert_batch_acceptance,
    assert_batch_results_contract,
    assert_http_status,
    json_body,
)


@pytest.mark.rest
def test_batch_scoring_rest_submit_and_get_results(http_client, config, db_client, batch_payload):
    response = http_client.post_json(config["service"]["rest_batch_path"], batch_payload)
    assert_http_status(response, 202)

    accepted = json_body(response)
    assert_batch_acceptance(accepted, batch_payload["batchId"], len(batch_payload["records"]))

    result_response = http_client.get(f"{config['service']['rest_batch_path']}/{batch_payload['batchId']}")
    assert_http_status(result_response, 200)

    result_body = json_body(result_response)
    assert_batch_results_contract(
        result_body,
        config["model"]["accepted_decisions"],
        expected_count=len(batch_payload["records"]),
    )

    for row in result_body["results"]:
        assert row["model_code"] == batch_payload["modelCode"]

    db_count = db_client.scalar(
        "SELECT COUNT(*) AS count_value FROM batch_results WHERE batch_id = ?",
        (batch_payload["batchId"],),
    )
    assert db_count == len(batch_payload["records"])

