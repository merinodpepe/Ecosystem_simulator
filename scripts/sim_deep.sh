#!/usr/bin/env bash
set -e
export LC_NUMERIC=C
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

OUTPUT_DIR="output/deep_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  DEEP TEST: 375x502 grid, 365 days"
echo "  (Full Vall de Cardós resolution)"
echo "========================================"
START=$(date +%s.%N)
python3 src/run_simulation.py --grid 375 502 --days 365 --output "$OUTPUT_DIR"
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "========================================"
printf "  Time: %.2f seconds\n" "$ELAPSED"
echo "  Output: $OUTPUT_DIR"
echo "========================================"
