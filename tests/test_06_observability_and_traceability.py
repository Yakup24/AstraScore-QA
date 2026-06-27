from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from mock_service.server import _valid_correlation_id

from astrascore_qa.contracts import CORRELATION_ID_HEADER, assert_correlation_id, assert_http_status, json_body
from astrascore_qa.log_checker import LogChecker
from astrascore_qa.soap import render_template


@pytest.mark.smoke
def test_correlation_id_should_be_echoed_and_logged(http_client, config, log_file, project_root: Path):
    correlation_id = f"corr-{uuid4().hex[:12]}"
    transaction_id = f"TRX-{uuid4().hex[:10].upper()}"
    xml_request = render_template(
        project_root / "testdata" / "soap" / "realtime_score_request.xml",
        {
            "transaction_id": transaction_id,
            "customer_id": "C1002",
            "msisdn": "905551112233",
            "model_code": "CREDIT_RISK_V1",
            "channel": "WEB",
            "amount": 2500,
        },
    )

    response = http_client.post_xml(
        config["service"]["soap_realtime_path"],
        xml_request,
        headers={CORRELATION_ID_HEADER: correlation_id},
    )

    assert_http_status(response, 200)
    assert_correlation_id(response, correlation_id)
    assert LogChecker(log_file).contains(f"correlationId={correlation_id}")


def test_correlation_id_header_should_reject_response_splitting_payloads():
    assert _valid_correlation_id("corr-safe_123:abc.def") == "corr-safe_123:abc.def"
    assert _valid_correlation_id("corr-123\r\nX-Injected: true") is None
    assert _valid_correlation_id("corr-123\nX-Injected: true") is None
    assert _valid_correlation_id("corr-123\tbad") is None


@pytest.mark.smoke
def test_metrics_endpoint_should_report_runtime_counters(http_client, config, batch_payload):
    submit_response = http_client.post_json(config["service"]["rest_batch_path"], batch_payload)
    assert_http_status(submit_response, 202)

    metrics_response = http_client.get(config["observability"]["metrics_path"])
    assert_http_status(metrics_response, 200)
    metrics = json_body(metrics_response)

    assert metrics["service"] == "astrascore-qa-mock"
    assert metrics["uptimeSeconds"] >= 0
    assert metrics["batchResultRows"] >= len(batch_payload["records"])
    assert metrics["completedBatches"] >= 1

