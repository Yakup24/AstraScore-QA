from __future__ import annotations

import pytest


@pytest.mark.db
def test_batch_output_should_match_database_records(http_client, config, db_client, batch_payload, project_root):
    http_client.post_json(config["service"]["rest_batch_path"], batch_payload)

    sql = (project_root / "testdata" / "sql" / "batch_result_count.sql").read_text(encoding="utf-8")
    result_count = db_client.scalar(sql, (batch_payload["batchId"],))

    assert result_count == len(batch_payload["records"])

    rows = db_client.query_all(
        """
        SELECT customer_id, score, decision
        FROM batch_results
        WHERE batch_id = ?
        ORDER BY customer_id
        """,
        (batch_payload["batchId"],),
    )

    assert [row["customer_id"] for row in rows] == ["C1001", "C1002", "C1003"]
    assert rows[0]["decision"] == "APPROVE"
    assert rows[1]["decision"] == "REVIEW"
    assert rows[2]["decision"] == "REJECT"
