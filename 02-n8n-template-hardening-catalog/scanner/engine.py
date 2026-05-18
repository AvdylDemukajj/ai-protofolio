"""Core workflow security scanning engine."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import structlog

from scanner.graph import WorkflowGraph
from scanner.models import Issue, ScanResult, ScanSummary, Severity

logger = structlog.get_logger(__name__)

CREDENTIAL_REQUIRED_TYPES = (
    "postgres",
    "openai",
    "lmchatopenai",
    "httprequest",
)


class RulesConfig:
    def __init__(self, config: dict[str, Any]) -> None:
        self.raw = config
        self.version = config.get("version", "1.0")
        self.fail_on = Severity(config.get("fail_on_severity", "HIGH"))
        self.rules = config.get("rules", {})
        self.secret_patterns = config.get("secret_patterns", [])
        self.credential_node_types = config.get("credential_node_types", [])
        self.webhook_auth_markers = [m.lower() for m in config.get("webhook_auth_markers", [])]
        self.allowed_http_hosts = config.get("allowed_http_hosts", [])

    def rule_enabled(self, rule_id: str) -> bool:
        return self.rules.get(rule_id, {}).get("enabled", True)

    def rule_severity(self, rule_id: str, default: Severity) -> Severity:
        raw = self.rules.get(rule_id, {}).get("severity")
        return Severity(raw) if raw else default


class WorkflowScanner:
    def __init__(self, rules_path: Path | None = None) -> None:
        if rules_path is None:
            rules_path = Path(__file__).resolve().parent.parent / "rules" / "security_rules.json"
        with rules_path.open(encoding="utf-8") as handle:
            self.config = RulesConfig(json.load(handle))
        self._compiled_patterns = [
            (item["id"], item["label"], re.compile(item["pattern"]))
            for item in self.config.secret_patterns
        ]

    def scan_path(self, target: Path) -> ScanSummary:
        summary = ScanSummary()
        files = self._collect_workflow_files(target)
        if not files:
            logger.warning("no_workflow_files", path=str(target))
            return summary

        for file_path in files:
            result = self.scan_file(file_path)
            summary.results.append(result)
            summary.scanned_files += 1
            if result.status == "PASSED":
                summary.passed += 1
            elif result.status == "FAILED":
                summary.failed += 1
            else:
                summary.errors += 1

        return summary

    def scan_file(self, file_path: Path) -> ScanResult:
        logger.info("scanning_workflow", file=str(file_path))
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            return ScanResult(
                file=str(file_path),
                workflow_name=file_path.stem,
                status="ERROR",
                error_message=f"Invalid JSON: {exc}",
            )

        if not isinstance(data, dict) or "nodes" not in data:
            return ScanResult(
                file=str(file_path),
                workflow_name=file_path.stem,
                status="ERROR",
                error_message="Invalid n8n workflow format (missing nodes array)",
            )

        issues: list[Issue] = []
        nodes = data.get("nodes", [])
        graph = WorkflowGraph(nodes, data.get("connections", {}))

        for node in nodes:
            issues.extend(self._check_node(file_path, node, graph))

        issues.extend(self._check_workflow_settings(data, graph))

        status = "FAILED" if issues else "PASSED"
        return ScanResult(
            file=str(file_path),
            workflow_name=data.get("name", file_path.stem),
            status=status,
            issues=issues,
        )

    def _collect_workflow_files(self, target: Path) -> list[Path]:
        if target.is_file():
            return [target] if target.suffix.lower() == ".json" else []
        return sorted(target.rglob("*.json"))

    def _issue(
        self,
        rule_id: str,
        severity: Severity,
        node: dict[str, Any],
        message: str,
        recommendation: str,
    ) -> Issue:
        return Issue(
            rule_id=rule_id,
            severity=severity,
            node=node.get("name", "Unknown"),
            node_type=node.get("type", "unknown"),
            message=message,
            recommendation=recommendation,
        )

    def _check_node(
        self, file_path: Path, node: dict[str, Any], graph: WorkflowGraph
    ) -> list[Issue]:
        issues: list[Issue] = []
        node_type = node.get("type", "")
        params = node.get("parameters", {})
        params_str = json.dumps(params)
        credentials = node.get("credentials") or {}

        if self.config.rule_enabled("hardcoded_credentials"):
            issues.extend(self._check_hardcoded_secrets(node, params_str))

        if self.config.rule_enabled("hardcoded_slack_webhook"):
            issues.extend(self._check_slack_webhook(node, params_str))

        if self.config.rule_enabled("missing_credential_binding"):
            issues.extend(self._check_credential_binding(node, node_type, credentials, params_str))

        if self.config.rule_enabled("placeholder_credentials"):
            issues.extend(self._check_placeholder_credentials(node, credentials))

        if self.config.rule_enabled("insecure_http"):
            issues.extend(self._check_insecure_http(node, params_str))

        if self.config.rule_enabled("dangerous_code_execution") and "code" in node_type.lower():
            issues.extend(self._check_dangerous_code(node, params))

        if self.config.rule_enabled("shell_execution_nodes"):
            issues.extend(self._check_shell_nodes(node, node_type))

        if self.config.rule_enabled("public_webhooks") and node_type == "n8n-nodes-base.webhook":
            issues.extend(self._check_webhook_auth(node, graph))

        return issues

    def _check_workflow_settings(self, data: dict[str, Any], graph: WorkflowGraph) -> list[Issue]:
        issues: list[Issue] = []
        settings = data.get("settings") or {}
        pseudo_node = {"name": "Workflow Settings", "type": "workflow"}

        if self.config.rule_enabled("execution_settings"):
            if not settings.get("executionOrder"):
                issues.append(
                    self._issue(
                        "execution_settings",
                        self.config.rule_severity("execution_settings", Severity.LOW),
                        pseudo_node,
                        "executionOrder is not set in workflow settings",
                        "Set settings.executionOrder to 'v1' for predictable execution.",
                    )
                )

        if self.config.rule_enabled("missing_error_handling"):
            has_error_trigger = graph.has_node_type("errorTrigger")
            has_error_workflow = bool(settings.get("errorWorkflow"))
            if not has_error_trigger and not has_error_workflow:
                issues.append(
                    self._issue(
                        "missing_error_handling",
                        self.config.rule_severity("missing_error_handling", Severity.MEDIUM),
                        pseudo_node,
                        "No Error Trigger node or settings.errorWorkflow configured",
                        "Link workflow 03-style error handler via Settings → Error Workflow.",
                    )
                )

        return issues

    def _check_hardcoded_secrets(self, node: dict[str, Any], params_str: str) -> list[Issue]:
        issues: list[Issue] = []
        for pattern_id, label, compiled in self._compiled_patterns:
            if compiled.search(params_str):
                issues.append(
                    self._issue(
                        "hardcoded_credentials",
                        self.config.rule_severity("hardcoded_credentials", Severity.CRITICAL),
                        node,
                        f"{label} pattern detected in node parameters",
                        "Move secrets to n8n Credentials or environment variables.",
                    )
                )
        return issues

    def _check_slack_webhook(self, node: dict[str, Any], params_str: str) -> list[Issue]:
        if re.search(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+", params_str):
            if "{{" in params_str and "$env" in params_str:
                return []
            return [
                self._issue(
                    "hardcoded_slack_webhook",
                    self.config.rule_severity("hardcoded_slack_webhook", Severity.CRITICAL),
                    node,
                    "Hardcoded Slack incoming webhook URL in parameters",
                    "Use $env.SLACK_WEBHOOK_URL or n8n Credentials instead of a static URL.",
                )
            ]
        return []

    def _check_credential_binding(
        self,
        node: dict[str, Any],
        node_type: str,
        credentials: dict[str, Any],
        params_str: str,
    ) -> list[Issue]:
        lowered = node_type.lower()
        if not any(fragment in lowered for fragment in CREDENTIAL_REQUIRED_TYPES):
            return []

        if credentials:
            return []

        if "httprequest" in lowered and ("$env" in params_str or "{{$env" in params_str):
            return []

        if "Authorization" in params_str or "apiKey" in params_str:
            return []

        return [
            self._issue(
                "missing_credential_binding",
                self.config.rule_severity("missing_credential_binding", Severity.HIGH),
                node,
                "Integration node has no credentials block configured",
                "Create and assign n8n Credentials for this node before production import.",
            )
        ]

    def _check_placeholder_credentials(
        self, node: dict[str, Any], credentials: dict[str, Any]
    ) -> list[Issue]:
        issues: list[Issue] = []
        for cred in credentials.values():
            cred_id = str(cred.get("id", ""))
            if cred_id.upper() == "PLACEHOLDER" or cred_id == "PLACEHOLDER_ID":
                issues.append(
                    self._issue(
                        "placeholder_credentials",
                        self.config.rule_severity("placeholder_credentials", Severity.INFO),
                        node,
                        f"Credential '{cred.get('name', 'unknown')}' still uses PLACEHOLDER id",
                        "Bind a real credential in the n8n UI after import.",
                    )
                )
        return issues

    def _check_insecure_http(self, node: dict[str, Any], params_str: str) -> list[Issue]:
        issues: list[Issue] = []
        for match in re.finditer(r"http://([^\s\"'/]+)", params_str, re.IGNORECASE):
            host = match.group(1).split(":")[0].lower()
            if any(allowed in host for allowed in self.config.allowed_http_hosts):
                continue
            issues.append(
                self._issue(
                    "insecure_http",
                    self.config.rule_severity("insecure_http", Severity.HIGH),
                    node,
                    f"Insecure HTTP URL references host '{host}'",
                    "Use HTTPS for all external API and webhook endpoints.",
                )
            )
        return issues

    def _check_dangerous_code(self, node: dict[str, Any], params: dict[str, Any]) -> list[Issue]:
        code = str(params.get("jsCode", ""))
        dangerous = [
            ("eval(", "eval() execution"),
            ("Function(", "dynamic Function constructor"),
            ("child_process", "child_process module access"),
            ("execSync(", "execSync shell execution"),
            ("spawn(", "spawn shell execution"),
        ]
        issues: list[Issue] = []
        lowered = code.lower()
        for marker, label in dangerous:
            if marker.lower() in lowered:
                issues.append(
                    self._issue(
                        "dangerous_code_execution",
                        self.config.rule_severity("dangerous_code_execution", Severity.CRITICAL),
                        node,
                        f"Dangerous pattern in Code node: {label}",
                        "Remove dynamic execution; use safe transforms only.",
                    )
                )
        return issues

    def _check_shell_nodes(self, node: dict[str, Any], node_type: str) -> list[Issue]:
        if "executeCommand" in node_type or "executecommand" in node_type.lower():
            return [
                self._issue(
                    "shell_execution_nodes",
                    self.config.rule_severity("shell_execution_nodes", Severity.CRITICAL),
                    node,
                    "Execute Command node is not allowed in production templates",
                    "Replace with approved nodes or run commands outside n8n.",
                )
            ]
        return []

    def _check_webhook_auth(self, node: dict[str, Any], graph: WorkflowGraph) -> list[Issue]:
        node_name = node.get("name", "")
        reachable = graph.successors_within(node_name, max_depth=4)

        for name in reachable:
            successor = graph.get_node(name)
            if not successor:
                continue
            if "code" in (successor.get("type") or "").lower():
                code = str(successor.get("parameters", {}).get("jsCode", "")).lower()
                if any(marker in code for marker in self.config.webhook_auth_markers):
                    return []

        return [
            self._issue(
                "public_webhooks",
                self.config.rule_severity("public_webhooks", Severity.HIGH),
                node,
                "Webhook trigger has no authentication validation in downstream nodes",
                "Add a Code/IF node that validates X-Webhook-Secret or HMAC before processing.",
            )
        ]

    def should_fail_summary(self, summary: ScanSummary, threshold: Severity | None = None) -> bool:
        threshold = threshold or self.config.fail_on
        for result in summary.results:
            for issue in result.issues:
                if issue.severity.rank() >= threshold.rank():
                    return True
        return False
