"""CLI entry point for the n8n workflow hardening scanner."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import structlog

from scanner.engine import WorkflowScanner
from scanner.models import Severity
from scanner.reporters import format_text, write_report

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="n8n-hardening",
        description="Static security scanner for exported n8n workflow JSON files.",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to a workflow .json file or directory (scanned recursively).",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=None,
        help="Custom security_rules.json path (default: packaged rules/).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        dest="report_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file (e.g. reports/scan.sarif).",
    )
    parser.add_argument(
        "--fail-on",
        choices=[s.value for s in Severity],
        default=None,
        help="Exit code 1 if any issue meets or exceeds this severity.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout report (useful with --output only).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.target.exists():
        logger.error("target_not_found", path=str(args.target))
        return 2

    scanner = WorkflowScanner(rules_path=args.rules)
    summary = scanner.scan_path(args.target)

    threshold = Severity(args.fail_on) if args.fail_on else scanner.config.fail_on

    if args.output:
        write_report(summary, args.output, args.report_format)
        logger.info("report_written", path=str(args.output))

    if not args.quiet:
        if args.report_format == "text":
            print(format_text(summary))
        else:
            from scanner.reporters import format_json, format_sarif

            content = (
                format_sarif(summary)
                if args.report_format == "sarif"
                else format_json(summary)
            )
            print(content)

    if summary.errors > 0:
        return 2
    if scanner.should_fail_summary(summary, threshold):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
