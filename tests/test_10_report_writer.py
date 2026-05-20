from __future__ import annotations

import json

import pytest

from astrascore_qa.report import ReportCaseResult, build_report, summarize_results, write_json_report


@pytest.mark.report
def test_report_writer_creates_json_report(tmp_path):
    report_path = tmp_path / "scoring-report.json"
    results = [
        ReportCaseResult(case_id="CONTRACT-001", suite="contract", status="passed"),
        ReportCaseResult(
            case_id="REGRESSION-001",
            suite="regression",
            status="failed",
            reason="actual score exceeded allowed tolerance",
            metadata={"expectedScore": 518, "actualScore": 531},
        ),
    ]

    written_path = write_json_report(report_path, "scoring-regression", "demo", results)

    report = json.loads(written_path.read_text(encoding="utf-8"))
    assert report["summary"] == {"total": 2, "passed": 1, "failed": 1, "skipped": 0}
    assert report["failures"][0]["caseId"] == "REGRESSION-001"


@pytest.mark.report
def test_report_builder_handles_empty_results():
    report = build_report("empty-suite", "demo", [])

    assert report["summary"] == {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    assert report["failures"] == []
    assert report["results"] == []


@pytest.mark.report
def test_report_summary_counts_skipped_results():
    summary = summarize_results(
        [
            ReportCaseResult(case_id="A", suite="smoke", status="passed"),
            ReportCaseResult(case_id="B", suite="smoke", status="failed"),
            ReportCaseResult(case_id="C", suite="smoke", status="skipped"),
        ]
    )

    assert summary == {"total": 3, "passed": 1, "failed": 1, "skipped": 1}
