#!/usr/bin/env bash
# Auto-patch qoder-autopilot with local fixes
set -e

PACKAGE_DIR=$(python3 -c "import qoder_autopilot; import os; print(os.path.dirname(qoder_autopilot.__file__))" 2>/dev/null || true)

if [ -z "$PACKAGE_DIR" ]; then
    echo "❌ qoder-autopilot not installed. Run: pip install qoder-autopilot"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for pair in "register.py:" "cli.py:" "otp.py:" "cli_login.py:auth" "anti_vm.py:infra" "machine_spoof.py:infra"; do
    SRC_NAME="${pair%%:*}"
    SUBDIR="${pair##*:}"
    SRC="$SCRIPT_DIR/$SRC_NAME"
    if [ "$SUBDIR" = "$SRC_NAME" ]; then
        DST="$PACKAGE_DIR/$SRC_NAME"
    else
        DST="$PACKAGE_DIR/$SUBDIR/$SRC_NAME"
    fi
    if [ -f "$SRC" ]; then
        mkdir -p "$(dirname "$DST")"
        cp "$DST" "$DST.bak.$(date +%s)" 2>/dev/null || true
        cp "$SRC" "$DST"
        echo "✅ Patched $DST"
    fi
done
