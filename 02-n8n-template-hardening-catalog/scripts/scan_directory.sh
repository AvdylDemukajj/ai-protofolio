#!/usr/bin/env bash
# Scan a directory of n8n workflow exports (CI-friendly).
set -euo pipefail

TARGET="${1:-../01-n8n-support-automation-pack/workflows}"
FORMAT="${FORMAT:-text}"
FAIL_ON="${FAIL_ON:-HIGH}"
OUTPUT="${OUTPUT:-./reports/scan.$(date +%Y%m%d_%H%M%S).${FORMAT}}"

mkdir -p "$(dirname "$OUTPUT")"

python -m scanner "$TARGET" \
  --format "$FORMAT" \
  --fail-on "$FAIL_ON" \
  --output "$OUTPUT"

echo "Report saved to $OUTPUT"
