#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUST_DIR="$SCRIPT_DIR/simulator"
VIZ_SCRIPT="$SCRIPT_DIR/src/visualize_simulation.py"
FIGURES_DIR="$SCRIPT_DIR/figures"

echo "============================================================"
echo "  Alt Pirineu Ecosystem Simulator"
echo "============================================================"
echo ""
echo "  Select mode:"
echo "    1) Ràpid  — 50×50, 30 dies (prova ràpida)"
echo "    2) Mig    — 100×100, 365 dies + figures"
echo "    3) Complet — 375×502, 365 dies + figures (pot trigar)"
echo ""
read -rp "  Mode [1-3]: " mode

case "$mode" in
  1)
    W=50; H=50; DAYS=30; OUTPUT="output_rapid"
    ;;
  2)
    W=100; H=100; DAYS=365; OUTPUT="output_mig"
    ;;
  3)
    W=375; H=502; DAYS=365; OUTPUT="output_complet"
    ;;
  *)
    echo "  Invalid option"; exit 1
    ;;
esac

echo ""
echo "  Running: ${W}×${H}, ${DAYS} dies"
echo "  Output:  ${OUTPUT}"
echo ""

cd "$RUST_DIR"
cargo run --release -- \
    --width "$W" --height "$H" \
    --days "$DAYS" \
    --output "$OUTPUT"

if [ "$mode" != "1" ]; then
    echo ""
    echo "  Generating figures..."
    mkdir -p "$FIGURES_DIR"
    cd "$SCRIPT_DIR"
    python3 "$VIZ_SCRIPT" \
        --dir "$RUST_DIR/$OUTPUT" \
        --save "$FIGURES_DIR"
fi

echo ""
echo "  Done!"
echo "  Data: $RUST_DIR/$OUTPUT"
echo "  Figures: $FIGURES_DIR"
echo "============================================================"
