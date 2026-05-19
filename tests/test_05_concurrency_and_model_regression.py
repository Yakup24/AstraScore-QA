from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import pytest

from astrascore_qa.soap import parse_score_response, render_template


def _send_realtime_request(
    http_client,
    soap_path: str,
    template_path: Path,
    customer_id: str,
    amount: int,
) -> tuple[int, dict, float]:
    transaction_id = f"TRX-{uuid4().hex[:10].upper()}"
    xml_request = render_template(
        template_path,
        {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "msisdn": "905551112233",
            "model_code": "CREDIT_RISK_V1",
            "channel": "WEB",
            "amount": amount,
        },
    )
    started = perf_counter()
    response = http_client.post_xml(soap_path, xml_request)
    duration = perf_counter() - started
    return response.status_code, parse_score_response(response.text), duration


@pytest.mark.performance
def test_realtime_scoring_concurrency_smoke(http_client, config, project_root: Path):
    template_path = project_root / "testdata" / "soap" / "realtime_score_request.xml"
    soap_path = config["service"]["soap_realtime_path"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(_send_realtime_request, http_client, soap_path, template_path, f"C20{i}", 1000 + i)
            for i in range(12)
        ]
        results = [future.result() for future in futures]

    assert all(status_code == 200 for status_code, _, _ in results)
    assert all(parsed["status"] == "SUCCESS" for _, parsed, _ in results)
    assert max(duration for _, _, duration in results) < 3


@pytest.mark.regression
def test_model_regression_scores_should_stay_in_expected_baseline(http_client, config, db_client, batch_payload):
    http_client.post_json(config["service"]["rest_batch_path"], batch_payload)

    rows = db_client.query_all(
        """
        SELECT br.customer_id, br.score, br.decision,
               mb.expected_min_score, mb.expected_max_score, mb.expected_decision
        FROM batch_results br
        JOIN model_baseline mb
          ON mb.customer_id = br.customer_id
         AND mb.model_code = br.model_code
        WHERE br.batch_id = ?
        ORDER BY br.customer_id
        """,
        (batch_payload["batchId"],),
    )

    assert rows, "Baseline records must exist for regression control."
    for row in rows:
        assert row["expected_min_score"] <= row["score"] <= row["expected_max_score"], row
        assert row["decision"] == row["expected_decision"], row

