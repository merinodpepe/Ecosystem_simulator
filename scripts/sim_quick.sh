#!/usr/bin/env bash
set -e
export LC_NUMERIC=C
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

OUTPUT_DIR="output/quick_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  QUICK TEST: 100x100 grid, 30 days"
echo "========================================"
START=$(date +%s.%N)
python3 src/run_simulation.py --grid 100 100 --days 30 --output "$OUTPUT_DIR"
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "========================================"
printf "  Time: %.2f seconds\n" "$ELAPSED"
echo "  Output: $OUTPUT_DIR"
echo "========================================"
