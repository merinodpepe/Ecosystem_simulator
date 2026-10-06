#!/usr/bin/env bash
set -e
export LC_NUMERIC=C
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

OUTPUT_DIR="output/medium_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  MEDIUM TEST: 200x200 grid, 365 days"
echo "========================================"
START=$(date +%s.%N)
python3 src/run_simulation.py --grid 200 200 --days 365 --output "$OUTPUT_DIR"
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "========================================"
printf "  Time: %.2f seconds\n" "$ELAPSED"
echo "  Output: $OUTPUT_DIR"
echo "========================================"
