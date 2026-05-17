# Tool Usage Policy

## Allowed Tools
- `get_ticket_status`: Always allowed (Read-only).
- `update_ticket_status`: Restricted based on `ALLOW_DESTRUCTIVE_ACTIONS`.
- `assign_ticket`: Restricted to managers only (future enhancement).

## Restrictions
- No bulk operations (e.g., "Close all tickets").
- No deletion of historical data.