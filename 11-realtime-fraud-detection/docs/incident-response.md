# Incident Response Plan

## High Risk Score (>0.9)
- Action: Automatic Rejection.
- Notification: Email sent to security team.

## Medium Risk Score (0.7 - 0.9)
- Action: Flag for Manual Review.
- Workflow: Analyst reviews via API Dashboard within 15 mins.

## False Positive Handling
- If an alert is marked as 'false_positive', the transaction is unblocked and the feedback is logged for model retraining.