#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DAYS=100
WIDTH=200
HEIGHT=200
RES=25
OUTPUT="output_medium"

rm -rf "$OUTPUT"

echo "============================================"
echo "  MEDIUM TEST: ${WIDTH}x${HEIGHT} grid, ${DAYS} days"
echo "============================================"

START=$(date +%s.%N)
cargo run --release -- \
    --width "$WIDTH" --height "$HEIGHT" \
    --days "$DAYS" --res "$RES" --output "$OUTPUT"
END=$(date +%s.%N)

ELAPSED=$(python3 -c "print(f'{float($END) - float($START):.3f}')")
RATE=$(python3 -c "print(f'{$DAYS / (float($END) - float($START)):.1f}')")

echo "============================================"
echo "  TIME: ${ELAPSED}s"
echo "  Rate: ${RATE} days/s"
echo "============================================"
