# Scan a directory of n8n workflow exports (CI-friendly).
param(
    [string]$Target = "..\01-n8n-support-automation-pack\workflows",
    [string]$Format = "sarif",
    [string]$FailOn = "HIGH"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = Join-Path $PSScriptRoot "..\reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$output = Join-Path $reportDir "scan.$timestamp.$Format"

Push-Location (Join-Path $PSScriptRoot "..")
try {
    python -m scanner $Target --format $Format --fail-on $FailOn --output $output
    Write-Host "Report saved to $output"
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
