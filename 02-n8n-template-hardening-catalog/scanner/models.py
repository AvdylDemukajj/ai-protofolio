"""Data models for workflow security scan results."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    def rank(self) -> int:
        order = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        return order[self]


class Issue(BaseModel):
    rule_id: str
    severity: Severity
    node: str
    node_type: str
    message: str
    recommendation: str


class ScanResult(BaseModel):
    file: str
    workflow_name: str
    status: str
    issues: list[Issue] = Field(default_factory=list)
    error_message: str | None = None

    @property
    def issues_count(self) -> int:
        return len(self.issues)

    def highest_severity(self) -> Severity | None:
        if not self.issues:
            return None
        return max(self.issues, key=lambda i: i.severity.rank()).severity


class ScanSummary(BaseModel):
    scanned_files: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[ScanResult] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
