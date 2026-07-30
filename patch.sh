#!/usr/bin/env bash
# Auto-patch qoder-autopilot with local fixes
set -e

PACKAGE_DIR=$(python3 -c "import qoder_autopilot; import os; print(os.path.dirname(qoder_autopilot.__file__))" 2>/dev/null || true)

if [ -z "$PACKAGE_DIR" ]; then
    echo "❌ qoder-autopilot not installed. Run: pip install qoder-autopilot"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for f in register.py cli.py otp.py; do
    SRC="$SCRIPT_DIR/$f"
    DST="$PACKAGE_DIR/$f"
    if [ -f "$SRC" ]; then
        cp "$DST" "$DST.bak.$(date +%s)" 2>/dev/null || true
        cp "$SRC" "$DST"
        echo "✅ Patched $DST"
    fi
done
