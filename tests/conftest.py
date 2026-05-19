from __future__ import annotations

import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from mock_service.server import MockScoringServer  # noqa: E402
from scripts.init_db import init_database  # noqa: E402

from astrascore_qa.config import load_config  # noqa: E402
from astrascore_qa.db import SQLiteClient  # noqa: E402
from astrascore_qa.http_client import HttpClient  # noqa: E402


def pytest_configure(config: pytest.Config) -> None:
    config.scoring_started_at = time.perf_counter()  # type: ignore[attr-defined]
    config.scoring_results = []  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    item.config.scoring_results.append(  # type: ignore[attr-defined]
        {
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "durationSeconds": round(report.duration, 4),
            "markers": sorted(mark.name for mark in item.iter_markers()),
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results: list[dict[str, Any]] = session.config.scoring_results  # type: ignore[attr-defined]
    counts = {
        "passed": sum(1 for result in results if result["outcome"] == "passed"),
        "failed": sum(1 for result in results if result["outcome"] == "failed"),
        "skipped": sum(1 for result in results if result["outcome"] == "skipped"),
    }
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "exitStatus": exitstatus,
        "durationSeconds": round(time.perf_counter() - session.config.scoring_started_at, 3),  # type: ignore[attr-defined]
        "baseUrl": os.getenv("SCORING_BASE_URL"),
        "databasePath": os.getenv("SCORING_DB_PATH"),
        "counts": counts,
        "tests": results,
    }
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "test_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_runtime(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    runtime_dir = tmp_path_factory.mktemp("scoring-runtime")
    db_path = runtime_dir / "scoring.db"
    log_file = runtime_dir / "astrascore_qa.log"
    init_database(db_path)
    os.environ["SCORING_DB_PATH"] = str(db_path)
    os.environ["SCORING_LOG_FILE"] = str(log_file)
    return {"db_path": db_path, "log_file": log_file}


@pytest.fixture(scope="session")
def mock_server(test_runtime: dict[str, Any]) -> MockScoringServer:
    port = _free_port()
    server = MockScoringServer(port=port, db_path=test_runtime["db_path"], log_file=test_runtime["log_file"])
    server.start()
    os.environ["SCORING_BASE_URL"] = server.base_url
    yield server
    server.stop()


@pytest.fixture()
def config(mock_server: MockScoringServer) -> dict[str, Any]:
    return load_config(PROJECT_ROOT / "config" / "config.yaml")


@pytest.fixture()
def http_client(config: dict[str, Any]) -> HttpClient:
    timeouts = config["timeouts"]
    http = config.get("http", {})
    return HttpClient(
        base_url=config["service"]["base_url"],
        timeout=(timeouts["connect_seconds"], timeouts["read_seconds"]),
        retries=http.get("retries", 0),
        retry_backoff_seconds=http.get("retry_backoff_seconds", 0),
        default_headers={"User-Agent": "astrascore-qa-tests/2.1"},
    )


@pytest.fixture()
def db_client(test_runtime: dict[str, Any]) -> SQLiteClient:
    return SQLiteClient(test_runtime["db_path"])


@pytest.fixture()
def log_file(test_runtime: dict[str, Any]) -> Path:
    return Path(test_runtime["log_file"])


@pytest.fixture()
def batch_payload(project_root: Path) -> dict[str, Any]:
    payload_path = project_root / "testdata" / "rest" / "batch_score_request.json"
    return json.loads(payload_path.read_text(encoding="utf-8"))


