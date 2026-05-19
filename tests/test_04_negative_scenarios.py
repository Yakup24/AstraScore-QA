from __future__ import annotations

import pytest

from astrascore_qa.contracts import assert_http_status, json_body
from astrascore_qa.soap import is_soap_fault, render_template


@pytest.mark.negative
def test_realtime_scoring_should_return_fault_when_transaction_id_missing(http_client, config, project_root):
    xml_request = render_template(
        project_root / "testdata" / "soap" / "realtime_score_request.xml",
        {
            "transaction_id": "",
            "customer_id": "C1001",
            "msisdn": "905551112233",
            "model_code": "CREDIT_RISK_V1",
            "channel": "MOBILE",
            "amount": 1500,
        },
    )

    response = http_client.post_xml(config["service"]["soap_realtime_path"], xml_request)

    assert_http_status(response, 400)
    assert is_soap_fault(response.text)
    assert "transactionId is required" in response.text


@pytest.mark.negative
def test_batch_scoring_should_reject_empty_record_list(http_client, config):
    payload = {
        "batchId": "BATCH-EMPTY-001",
        "modelCode": "CREDIT_RISK_V1",
        "records": [],
    }

    response = http_client.post_json(config["service"]["rest_batch_path"], payload)

    assert_http_status(response, 400)
    body = json_body(response)
    assert body["status"] == "FAILED"
    assert body["errorCode"] == "EMPTY_RECORDS"
    assert "records cannot be empty" in body["error"]


@pytest.mark.negative
def test_batch_scoring_should_reject_invalid_amount(http_client, config):
    payload = {
        "batchId": "BATCH-BAD-AMOUNT-001",
        "modelCode": "CREDIT_RISK_V1",
        "records": [{"customerId": "C1001", "amount": "not-a-number"}],
    }

    response = http_client.post_json(config["service"]["rest_batch_path"], payload)

    assert_http_status(response, 400)
    body = json_body(response)
    assert body["status"] == "FAILED"
    assert body["errorCode"] == "INVALID_AMOUNT"


@pytest.mark.negative
def test_batch_scoring_should_reject_malformed_json(http_client, config):
    response = http_client.request(
        "POST",
        config["service"]["rest_batch_path"],
        data=b"{invalid-json",
        headers={"Content-Type": "application/json"},
    )

    assert_http_status(response, 400)
    body = json_body(response)
    assert body["status"] == "FAILED"
    assert body["errorCode"] == "INVALID_JSON"

