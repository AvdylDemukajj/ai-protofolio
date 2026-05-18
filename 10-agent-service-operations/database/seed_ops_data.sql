-- Sample operational data for demos and integration tests
INSERT INTO support_tickets (ticket_id_str, subject, status, priority, assigned_to)
VALUES
    ('TICK-101', 'VPN not connecting for remote staff', 'Open', 'High', 'network-ops'),
    ('TICK-102', 'Billing portal shows wrong plan', 'In Progress', 'Medium', 'billing-team'),
    ('TICK-103', 'API latency spike in EU region', 'Open', 'Critical', 'sre-oncall'),
    ('TICK-104', 'Password reset emails delayed', 'Resolved', 'Low', 'identity-team')
ON CONFLICT (ticket_id_str) DO NOTHING;

INSERT INTO audit_logs (action_type, target_resource, parameters, agent_decision, guardrail_triggered)
VALUES
    (
        'POLICY_CHECK',
        'TICK-103',
        '{"action":"update_status","requested_status":"Closed"}',
        'Blocked status change on critical ticket without approval.',
        TRUE
    ),
    (
        'TOOL_CALL',
        'TICK-102',
        '{"action":"assign","assignee":"billing-team"}',
        'Assigned ticket to billing-team.',
        FALSE
    );
