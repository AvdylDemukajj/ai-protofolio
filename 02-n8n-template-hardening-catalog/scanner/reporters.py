"""Report formatters for scan results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner.models import ScanSummary, Severity


def format_text(summary: ScanSummary) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("n8n Workflow Hardening Scan Report")
    lines.append("=" * 60)
    lines.append(
        f"Files: {summary.scanned_files} | Passed: {summary.passed} | "
        f"Failed: {summary.failed} | Errors: {summary.errors}"
    )
    lines.append("")

    for result in summary.results:
        lines.append("-" * 60)
        lines.append(f"Workflow: {result.workflow_name}")
        lines.append(f"File:     {result.file}")
        lines.append(f"Status:   {result.status}")
        if result.error_message:
            lines.append(f"Error:    {result.error_message}")
        elif result.issues:
            lines.append(f"Issues:   {result.issues_count}")
            for index, issue in enumerate(result.issues, 1):
                lines.append(
                    f"  {index}. [{issue.severity.value}] {issue.rule_id}: {issue.message}"
                )
                lines.append(f"     Node: {issue.node} ({issue.node_type})")
                lines.append(f"     Fix:  {issue.recommendation}")
        else:
            lines.append("Issues:   0 (clean)")
        lines.append("")

    return "\n".join(lines)


def format_json(summary: ScanSummary) -> str:
    return json.dumps(summary.to_dict(), indent=2, default=str)


def format_sarif(summary: ScanSummary) -> str:
    """SARIF 2.1.0 report for CI integrations (GitHub, Azure DevOps)."""
    rules: dict[str, Any] = {}
    results: list[dict[str, Any]] = []

    for scan in summary.results:
        for issue in scan.issues:
            rule_id = issue.rule_id
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": rule_id,
                    "shortDescription": {"text": issue.message},
                    "defaultConfiguration": {"level": _sarif_level(issue.severity)},
                }

            results.append(
                {
                    "ruleId": rule_id,
                    "level": _sarif_level(issue.severity),
                    "message": {"text": issue.message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": scan.file},
                            }
                        }
                    ],
                    "properties": {
                        "node": issue.node,
                        "nodeType": issue.node_type,
                        "recommendation": issue.recommendation,
                        "workflow": scan.workflow_name,
                    },
                }
            )

    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "n8n-workflow-hardening",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/n8n-io/n8n",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "invocations": [
                    {
                        "executionSuccessful": summary.errors == 0,
                        "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }
        ],
    }
    return json.dumps(sarif, indent=2)


def _sarif_level(severity: Severity) -> str:
    if severity in (Severity.CRITICAL, Severity.HIGH):
        return "error"
    if severity == Severity.MEDIUM:
        return "warning"
    return "note"


def write_report(summary: ScanSummary, output_path: Path, report_format: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if report_format == "json":
        content = format_json(summary)
    elif report_format == "sarif":
        content = format_sarif(summary)
    else:
        content = format_text(summary)
    output_path.write_text(content, encoding="utf-8")
