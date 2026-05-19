from __future__ import annotations

import json
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from defusedxml.ElementTree import fromstring

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "scoring.db"
DEFAULT_LOG_FILE = PROJECT_ROOT / "logs" / "astrascore_qa.log"
CORRELATION_ID_HEADER = "X-Correlation-ID"


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _xml_text(xml_body: str, local_name: str) -> str | None:
    root = fromstring(xml_body)
    for element in root.iter():
        if _strip_namespace(element.tag) == local_name:
            return element.text
    return None


def _stable_customer_score(customer_id: str, amount: float) -> int:
    """Deterministic demo scoring logic.

    Specific customer ids are pinned for regression demo. Unknown ids get a stable
    pseudo-score derived from characters and amount.
    """
    pinned_scores = {
        "C1001": 700,
        "C1002": 590,
        "C1003": 410,
    }
    if customer_id in pinned_scores:
        base = pinned_scores[customer_id]
    else:
        base = 350 + (sum(ord(char) for char in customer_id) % 430)

    amount_penalty = min(int(amount / 10000), 80)
    score = max(250, min(900, base - amount_penalty))
    return score


def _decision(score: int) -> str:
    if score >= 650:
        return "APPROVE"
    if score >= 500:
        return "REVIEW"
    return "REJECT"


def _log(message: str, log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp}\tINFO\t{message}\n")


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


class ScoringRequestHandler(BaseHTTPRequestHandler):
    server_version = "AstraScoreQAMock/2.1"

    def _send_json(self, status: int, payload: dict[str, Any], correlation_id: str | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if correlation_id:
            self.send_header(CORRELATION_ID_HEADER, correlation_id)
        self.end_headers()
        self.wfile.write(body)

    def _send_xml(self, status: int, body: str, correlation_id: str | None = None) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        if correlation_id:
            self.send_header(CORRELATION_ID_HEADER, correlation_id)
        self.end_headers()
        self.wfile.write(encoded)

    def _read_body(self) -> bytes:
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length)

    def _correlation_id(self) -> str:
        return self.headers.get(CORRELATION_ID_HEADER) or f"mock-{uuid4().hex[:12]}"

    @property
    def db_path(self) -> Path:
        return Path(self.server.db_path)

    @property
    def log_file(self) -> Path:
        return Path(self.server.log_file)

    @property
    def db_lock(self) -> threading.Lock:
        return self.server.db_lock

    def log_message(self, format: str, *args: Any) -> None:
        # Keep test output clean. Real request logs are written to custom log file.
        return

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        correlation_id = self._correlation_id()
        if parsed.path == "/health":
            self._send_json(200, {"status": "UP", "service": "astrascore-qa-mock"}, correlation_id)
            return

        if parsed.path == "/metrics":
            with self.db_lock, _connect(self.db_path) as connection:
                realtime_count = connection.execute("SELECT COUNT(*) FROM realtime_results").fetchone()[0]
                batch_result_count = connection.execute("SELECT COUNT(*) FROM batch_results").fetchone()[0]
                batch_count = connection.execute("SELECT COUNT(DISTINCT batch_id) FROM batch_results").fetchone()[0]
            started_at = float(getattr(self.server, "started_at", time.time()))
            self._send_json(
                200,
                {
                    "service": "astrascore-qa-mock",
                    "uptimeSeconds": round(time.time() - started_at, 3),
                    "realtimeRequests": realtime_count,
                    "batchResultRows": batch_result_count,
                    "completedBatches": batch_count,
                },
                correlation_id,
            )
            return

        if parsed.path.startswith("/api/v1/batch-scoring/"):
            batch_id = parsed.path.rsplit("/", 1)[-1]
            with self.db_lock, _connect(self.db_path) as connection:
                rows = connection.execute(
                    """
                    SELECT batch_id, customer_id, model_code, amount, score, decision, created_at
                    FROM batch_results
                    WHERE batch_id = ?
                    ORDER BY customer_id
                    """,
                    (batch_id,),
                ).fetchall()
            self._send_json(
                200,
                {
                    "batchId": batch_id,
                    "status": "COMPLETED" if rows else "NOT_FOUND",
                    "results": [dict(row) for row in rows],
                },
                correlation_id,
            )
            return

        self._send_json(404, {"error": "not_found", "path": parsed.path}, correlation_id)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        if parsed.path == "/soap/realtime-scoring":
            self._handle_soap_realtime()
            return
        if parsed.path == "/api/v1/batch-scoring":
            self._handle_batch_scoring()
            return
        self._send_json(404, {"error": "not_found", "path": parsed.path}, self._correlation_id())

    def _handle_soap_realtime(self) -> None:
        correlation_id = self._correlation_id()
        raw_body = self._read_body().decode("utf-8", errors="replace")
        try:
            transaction_id = _xml_text(raw_body, "transactionId")
            customer_id = _xml_text(raw_body, "customerId") or "UNKNOWN"
            msisdn = _xml_text(raw_body, "msisdn") or ""
            model_code = _xml_text(raw_body, "modelCode") or "CREDIT_RISK_V1"
            amount_text = _xml_text(raw_body, "amount") or "0"
            amount = float(amount_text)
        except Exception as exc:  # noqa: BLE001 - service fault simulation
            self._send_xml(400, self._soap_fault(f"Invalid SOAP request: {exc}"), correlation_id)
            return

        if not transaction_id:
            self._send_xml(400, self._soap_fault("transactionId is required"), correlation_id)
            return

        score = _stable_customer_score(customer_id, amount)
        decision = _decision(score)

        with self.db_lock, _connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO realtime_results
                (transaction_id, customer_id, msisdn, model_code, amount, score, decision, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (transaction_id, customer_id, msisdn, model_code, amount, score, decision),
            )
            connection.commit()

        _log(
            f"REALTIME_SCORE transactionId={transaction_id} customerId={customer_id} "
            f"modelCode={model_code} score={score} decision={decision} correlationId={correlation_id}",
            self.log_file,
        )

        transaction_id_xml = escape(transaction_id)
        model_code_xml = escape(model_code)
        decision_xml = escape(decision)
        response = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:sc=\"http://example.com/scoring\">
  <soapenv:Body>
    <sc:RealtimeScoringResponse>
      <transactionId>{transaction_id_xml}</transactionId>
      <status>SUCCESS</status>
      <modelCode>{model_code_xml}</modelCode>
      <modelVersion>1.0.0</modelVersion>
      <score>{score}</score>
      <decision>{decision_xml}</decision>
    </sc:RealtimeScoringResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        self._send_xml(200, response, correlation_id)

    def _handle_batch_scoring(self) -> None:
        correlation_id = self._correlation_id()
        raw_body = self._read_body().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw_body)
        except Exception as exc:  # noqa: BLE001 - service error simulation
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "INVALID_JSON", "error": f"Invalid JSON request: {exc}"},
                correlation_id,
            )
            return

        if not isinstance(payload, dict):
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "INVALID_PAYLOAD", "error": "payload must be a JSON object"},
                correlation_id,
            )
            return

        batch_id = payload.get("batchId")
        if not isinstance(batch_id, str) or not batch_id.strip():
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "MISSING_BATCH_ID", "error": "batchId is required"},
                correlation_id,
            )
            return

        model_code = payload.get("modelCode", "CREDIT_RISK_V1")
        if not isinstance(model_code, str) or not model_code.strip():
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "INVALID_MODEL_CODE", "error": "modelCode must be a string"},
                correlation_id,
            )
            return

        records = payload.get("records")
        if not isinstance(records, list):
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "INVALID_RECORDS", "error": "records must be a list"},
                correlation_id,
            )
            return

        if not records:
            self._send_json(
                400,
                {"status": "FAILED", "errorCode": "EMPTY_RECORDS", "error": "records cannot be empty"},
                correlation_id,
            )
            return

        normalized_records: list[dict[str, Any]] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                self._send_json(
                    400,
                    {
                        "status": "FAILED",
                        "errorCode": "INVALID_RECORD",
                        "error": f"records[{index}] must be a JSON object",
                    },
                    correlation_id,
                )
                return
            customer_id = record.get("customerId")
            if not isinstance(customer_id, str) or not customer_id.strip():
                self._send_json(
                    400,
                    {
                        "status": "FAILED",
                        "errorCode": "MISSING_CUSTOMER_ID",
                        "error": f"records[{index}].customerId is required",
                    },
                    correlation_id,
                )
                return
            try:
                amount = float(record.get("amount", 0))
            except (TypeError, ValueError):
                self._send_json(
                    400,
                    {
                        "status": "FAILED",
                        "errorCode": "INVALID_AMOUNT",
                        "error": f"records[{index}].amount must be numeric",
                    },
                    correlation_id,
                )
                return
            if amount < 0:
                self._send_json(
                    400,
                    {
                        "status": "FAILED",
                        "errorCode": "INVALID_AMOUNT",
                        "error": f"records[{index}].amount must be non-negative",
                    },
                    correlation_id,
                )
                return
            normalized_records.append({"customerId": customer_id, "amount": amount})

        output_rows: list[dict[str, Any]] = []
        with self.db_lock, _connect(self.db_path) as connection:
            connection.execute("DELETE FROM batch_results WHERE batch_id = ?", (batch_id,))
            for record in normalized_records:
                customer_id = str(record["customerId"])
                amount = float(record["amount"])
                score = _stable_customer_score(customer_id, amount)
                decision = _decision(score)
                connection.execute(
                    """
                    INSERT INTO batch_results
                    (batch_id, customer_id, model_code, amount, score, decision, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (batch_id, customer_id, model_code, amount, score, decision),
                )
                output_rows.append(
                    {
                        "batchId": batch_id,
                        "customerId": customer_id,
                        "modelCode": model_code,
                        "amount": amount,
                        "score": score,
                        "decision": decision,
                    }
                )
            connection.commit()

        _log(
            f"BATCH_SCORE batchId={batch_id} modelCode={model_code} totalRecords={len(records)} "
            f"correlationId={correlation_id}",
            self.log_file,
        )
        self._send_json(
            202,
            {
                "batchId": batch_id,
                "status": "ACCEPTED",
                "totalRecords": len(output_rows),
                "correlationId": correlation_id,
            },
            correlation_id,
        )

    @staticmethod
    def _soap_fault(message: str) -> str:
        safe_message = escape(message)
        return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>soapenv:Client</faultcode>
      <faultstring>{safe_message}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""


class MockScoringServer:
    """Thread-friendly wrapper used by pytest fixtures."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8089,
        db_path: str | Path | None = None,
        log_file: str | Path | None = None,
    ):
        self.host = host
        self.port = port
        self.db_path = Path(db_path or os.getenv("SCORING_DB_PATH", DEFAULT_DB_PATH))
        self.log_file = Path(log_file or os.getenv("SCORING_LOG_FILE", DEFAULT_LOG_FILE))
        self.httpd: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> None:
        self.httpd = ThreadingHTTPServer((self.host, self.port), ScoringRequestHandler)
        self.httpd.db_path = self.db_path  # type: ignore[attr-defined]
        self.httpd.log_file = self.log_file  # type: ignore[attr-defined]
        self.httpd.db_lock = threading.Lock()  # type: ignore[attr-defined]
        self.httpd.started_at = time.time()  # type: ignore[attr-defined]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.1)

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread:
            self.thread.join(timeout=2)


def main() -> None:
    db_path = Path(os.getenv("SCORING_DB_PATH", DEFAULT_DB_PATH))
    if not db_path.exists():
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.init_db import init_database

        init_database(db_path)
    server = MockScoringServer(db_path=db_path)
    print(f"Mock scoring server started at {server.base_url}")
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock scoring server...")
        server.stop()


if __name__ == "__main__":
    main()

