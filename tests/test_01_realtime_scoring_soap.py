from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from astrascore_qa.contracts import CORRELATION_ID_HEADER, assert_http_status, assert_score_contract, json_body
from astrascore_qa.log_checker import LogChecker
from astrascore_qa.soap import parse_score_response, render_template


@pytest.mark.smoke
def test_health_check(http_client, config):
    response = http_client.get(config["service"]["health_path"])

    assert_http_status(response, 200)
    assert json_body(response)["status"] == "UP"
    assert CORRELATION_ID_HEADER in response.headers


@pytest.mark.soap
def test_realtime_scoring_soap_success(http_client, config, db_client, log_file, project_root: Path):
    transaction_id = f"TRX-{uuid4().hex[:10].upper()}"
    xml_request = render_template(
        project_root / "testdata" / "soap" / "realtime_score_request.xml",
        {
            "transaction_id": transaction_id,
            "customer_id": "C1001",
            "msisdn": "905551112233",
            "model_code": "CREDIT_RISK_V1",
            "channel": "MOBILE",
            "amount": 1500,
        },
    )

    response = http_client.post_xml(config["service"]["soap_realtime_path"], xml_request, soap_action="RealtimeScoring")
    parsed = parse_score_response(response.text)

    assert_http_status(response, 200)
    assert parsed["transaction_id"] == transaction_id
    assert parsed["status"] == "SUCCESS"
    assert parsed["model_code"] == "CREDIT_RISK_V1"
    assert_score_contract(parsed, config["model"]["accepted_decisions"])
    assert CORRELATION_ID_HEADER in response.headers

    db_row = db_client.query_one(
        "SELECT transaction_id, customer_id, score, decision FROM realtime_results WHERE transaction_id = ?",
        (transaction_id,),
    )
    assert db_row is not None
    assert db_row["customer_id"] == "C1001"
    assert db_row["score"] == parsed["score"]
    assert db_row["decision"] == parsed["decision"]

    assert LogChecker(log_file).contains(transaction_id)

