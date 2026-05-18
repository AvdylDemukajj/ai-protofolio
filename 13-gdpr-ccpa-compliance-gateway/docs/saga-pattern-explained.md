# Saga Pattern Implementation

## Why Saga?
In a microservices architecture, we cannot use ACID transactions across different databases (Postgres vs S3 vs External APIs).

## Flow
1. **Delete from Analytics** -> Success
2. **Delete from S3** -> **FAIL**
3. **Compensate**: Trigger logic to "undo" or flag the Analytics deletion for manual review.
4. **Alert**: Notify engineering team via Slack/PagerDuty.

This ensures the system never stays in an unknown state.