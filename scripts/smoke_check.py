from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from astrascore_qa.config import load_config  # noqa: E402
from astrascore_qa.contracts import CORRELATION_ID_HEADER  # noqa: E402
from astrascore_qa.http_client import HttpClient  # noqa: E402


def build_client(config_path: Path | None = None) -> tuple[HttpClient, dict]:
    config = load_config(config_path)
    timeouts = config["timeouts"]
    http = config.get("http", {})
    return (
        HttpClient(
            base_url=config["service"]["base_url"],
            timeout=(timeouts["connect_seconds"], timeouts["read_seconds"]),
            retries=http.get("retries", 0),
            retry_backoff_seconds=http.get("retry_backoff_seconds", 0),
            default_headers={"User-Agent": "astrascore-qa-smoke/2.1"},
        ),
        config,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a scoring service health smoke check.")
    parser.add_argument("--config", type=Path, default=None, help="Optional path to config.yaml")
    args = parser.parse_args()

    client, config = build_client(args.config)
    correlation_id = f"smoke-{uuid4().hex[:12]}"
    correlation_header = config.get("observability", {}).get("correlation_header", CORRELATION_ID_HEADER)
    response = client.get(
        config["service"]["health_path"],
        headers={correlation_header: correlation_id},
    )
    is_json = response.headers.get("Content-Type", "").startswith("application/json")
    payload = {
        "ok": response.status_code == 200 and response.headers.get(correlation_header) == correlation_id,
        "statusCode": response.status_code,
        "baseUrl": config["service"]["base_url"],
        "correlationId": response.headers.get(correlation_header),
        "body": response.json() if is_json else response.text,
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


