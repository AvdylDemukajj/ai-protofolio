# Dead Letter Queue (DLQ) Policy

## Trigger Conditions
A task is moved to DLQ if:
1. It fails `MAX_RETRIES` (default 3) times.
2. The error is non-recoverable (e.g., file format unsupported).

## Handling DLQ Items
1. **Manual Review**: Engineers inspect DLQ items via Redis CLI or a future Admin UI.
2. **Replay**: If the issue was transient (e.g., DB down), tasks can be moved back to the main queue.
3. **Archival**: Failed documents are archived in S3 under `failed/` prefix for compliance.