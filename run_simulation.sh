#!/bin/bash
set -euo pipefail

# Alt Pirineu Ecosystem Simulator - Run Script
# Usage: ./run_simulation.sh [--full] [--days 365] [--output custom_output]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUST_DIR="$SCRIPT_DIR/simulator"
VIZ_SCRIPT="$SCRIPT_DIR/src/visualize_simulation.py"
FIGURES_DIR="$SCRIPT_DIR/figures"

RUN_FULL=false
DAYS=365
OUTPUT="output"
RUST_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --full) RUN_FULL=true; shift ;;
        --days) DAYS="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) RUST_ARGS+=("$1"); shift ;;
    esac
done

mkdir -p "$FIGURES_DIR"

echo "============================================================"
echo "  Alt Pirineu Ecosystem Simulator"
echo "============================================================"

if [ "$RUN_FULL" = true ]; then
    echo "  Running FULL-SCALE simulation (375x502 grid)"
    cd "$RUST_DIR"
    cargo run --release -- \
        --width 375 --height 502 \
        --days "$DAYS" \
        --output "$OUTPUT" \
        "${RUST_ARGS[@]}"
else
    echo "  Running TEST simulation (100x100 grid)"
    cd "$RUST_DIR"
    cargo run --release -- \
        --width 100 --height 100 \
        --days "$DAYS" \
        --output "$OUTPUT" \
        "${RUST_ARGS[@]}"
fi

echo ""
echo "  Generating visualizations..."
cd "$SCRIPT_DIR"
python3 "$VIZ_SCRIPT" \
    --dir "$OUTPUT" \
    --save "$FIGURES_DIR"

echo ""
echo "  Done! Figures saved to: $FIGURES_DIR"
echo "  Simulation data: $RUST_DIR/$OUTPUT"
echo "============================================================"
