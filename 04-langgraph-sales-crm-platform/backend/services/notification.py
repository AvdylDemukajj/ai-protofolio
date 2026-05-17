def send_slack_notification(message: str):
    """Sends a notification to Slack."""
    print(f"🔔 Slack Notification: {message}")
    # Implementation: requests.post(SLACK_WEBHOOK, json={"text": message})

def send_email_draft(to: str, draft: str):
    """Simulates sending the drafted email."""
    print(f"📧 Sending email to {to}: {draft[:50]}...")