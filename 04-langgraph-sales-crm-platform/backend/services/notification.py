"""Outbound notifications (Slack, email simulation)."""

from __future__ import annotations

import httpx
import structlog

from backend.config import settings

logger = structlog.get_logger(__name__)


def send_slack_notification(message: str) -> bool:
    """Post message to Slack incoming webhook when configured."""
    url = settings.SLACK_WEBHOOK_URL
    if not url:
        logger.info("slack_skipped", reason="SLACK_WEBHOOK_URL not set", message=message)
        return False
    try:
        response = httpx.post(url, json={"text": message}, timeout=10.0)
        response.raise_for_status()
        logger.info("slack_sent")
        return True
    except Exception as exc:
        logger.error("slack_failed", error=str(exc))
        return False


def send_email_draft(to_email: str, subject: str, body: str) -> bool:
    """Simulate email send — integrate SES/SendGrid in production."""
    logger.info(
        "email_simulated",
        to=to_email,
        subject=subject,
        preview=body[:80],
    )
    return True
