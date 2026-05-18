# Test the support-intake webhook (activate workflow 01 in n8n first).
$ErrorActionPreference = "Stop"

$WebhookUrl = if ($env:WEBHOOK_URL) { $env:WEBHOOK_URL } else { "http://localhost:5678/webhook/support-intake" }
$WebhookSecret = $env:WEBHOOK_SECRET
if (-not $WebhookSecret) {
    throw "Set WEBHOOK_SECRET in your environment or .env file."
}

$body = @{
    customer_email = "test.user@example.com"
    subject        = "Urgent refund - charged twice"
    body           = "I was charged twice for invoice #999. Please refund immediately."
    external_id    = "test-webhook-001"
} | ConvertTo-Json

$headers = @{
    "Content-Type"     = "application/json"
    "X-Webhook-Secret" = $WebhookSecret
}

$response = Invoke-RestMethod -Uri $WebhookUrl -Method Post -Headers $headers -Body $body
$response | ConvertTo-Json -Depth 5
Write-Host ""
Write-Host "Run: python scripts/validate_tickets.py"
