# Test lead webhook intake (activate workflow 01 first).
$ErrorActionPreference = "Stop"

$WebhookUrl = "http://localhost:5679/webhook/lead-intake"
if ($env:WEBHOOK_URL) {
    $base = $env:WEBHOOK_URL.TrimEnd("/")
    if ($base -match "lead-intake") {
        $WebhookUrl = $base
    } else {
        $WebhookUrl = "$base/webhook/lead-intake"
    }
}

$WebhookSecret = $env:WEBHOOK_SECRET
if (-not $WebhookSecret) {
    throw "Set WEBHOOK_SECRET in your .env file."
}

$body = @{
    name         = "Jane CTO"
    email        = "jane.cto@enterprise.io"
    company      = "Enterprise IO"
    company_size = 250
    message      = "We need AI lead routing for our sales team this quarter."
    source       = "website"
    external_id  = "test-lead-001"
} | ConvertTo-Json

$headers = @{
    "Content-Type"     = "application/json"
    "X-Webhook-Secret" = $WebhookSecret
}

Invoke-RestMethod -Uri $WebhookUrl -Method Post -Headers $headers -Body $body | ConvertTo-Json
Write-Host ""
Write-Host "Run: python scripts/validate_leads.py"
