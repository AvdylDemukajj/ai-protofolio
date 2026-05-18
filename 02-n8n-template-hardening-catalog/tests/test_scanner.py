"""Unit tests for the workflow hardening scanner."""

from pathlib import Path

import pytest

from scanner.engine import WorkflowScanner
from scanner.models import Severity

FIXTURES = Path(__file__).parent / "fixtures"
RULES = Path(__file__).resolve().parent.parent / "rules" / "security_rules.json"


@pytest.fixture
def scanner() -> WorkflowScanner:
    return WorkflowScanner(rules_path=RULES)


def test_insecure_webhook_fails_public_webhook_rule(scanner: WorkflowScanner) -> None:
    result = scanner.scan_file(FIXTURES / "insecure_webhook.json")
    assert result.status == "FAILED"
    rule_ids = {issue.rule_id for issue in result.issues}
    assert "public_webhooks" in rule_ids


def test_secure_webhook_passes_auth_check(scanner: WorkflowScanner) -> None:
    result = scanner.scan_file(FIXTURES / "secure_webhook.json")
    public_issues = [i for i in result.issues if i.rule_id == "public_webhooks"]
    assert public_issues == []


def test_hardcoded_openai_key_is_critical(scanner: WorkflowScanner) -> None:
    result = scanner.scan_file(FIXTURES / "hardcoded_secrets.json")
    assert result.status == "FAILED"
    critical = [i for i in result.issues if i.rule_id == "hardcoded_credentials"]
    assert critical
    assert critical[0].severity == Severity.CRITICAL


def test_scan_directory_summary(scanner: WorkflowScanner) -> None:
    summary = scanner.scan_path(FIXTURES)
    assert summary.scanned_files == 3
    assert summary.failed >= 2


def test_cli_exit_code_fail_on_high(tmp_path: Path) -> None:
    from scanner.cli import main

    code = main([str(FIXTURES / "hardcoded_secrets.json"), "--fail-on", "HIGH", "--quiet"])
    assert code == 1


def test_sarif_report_contains_results(scanner: WorkflowScanner) -> None:
    from scanner.reporters import format_sarif

    summary = scanner.scan_path(FIXTURES / "insecure_webhook.json")
    sarif = format_sarif(summary)
    assert "runs" in sarif
    assert "public_webhooks" in sarif
