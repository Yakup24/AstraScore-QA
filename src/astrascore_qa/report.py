from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReportCaseResult:
    case_id: str
    status: str
    suite: str
    reason: str | None = None
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "caseId": self.case_id,
            "suite": self.suite,
            "status": self.status,
            "reason": self.reason,
            "durationSeconds": self.duration_seconds,
            "metadata": self.metadata,
        }


def summarize_results(results: list[ReportCaseResult]) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.status == "passed"),
        "failed": sum(1 for result in results if result.status == "failed"),
        "skipped": sum(1 for result in results if result.status == "skipped"),
    }


def build_report(
    suite: str,
    environment: str,
    results: list[ReportCaseResult],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failures = [result.as_dict() for result in results if result.status == "failed"]
    return {
        "suite": suite,
        "environment": environment,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": summarize_results(results),
        "failures": failures,
        "results": [result.as_dict() for result in results],
        "metadata": metadata or {},
    }


def write_json_report(
    path: str | Path,
    suite: str,
    environment: str,
    results: list[ReportCaseResult],
    metadata: dict[str, Any] | None = None,
) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(suite=suite, environment=environment, results=results, metadata=metadata)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path
