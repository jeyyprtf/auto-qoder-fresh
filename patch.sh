#!/usr/bin/env bash
# Auto-patch qoder-autopilot register.py with slower delays + fixed button click
set -e

# Find installed package location
PACKAGE_DIR=$(python3 -c "import qoder_autopilot; import os; print(os.path.dirname(qoder_autopilot.__file__))" 2>/dev/null || true)

if [ -z "$PACKAGE_DIR" ]; then
    echo "❌ qoder-autopilot not installed. Run: pip install qoder-autopilot"
    exit 1
fi

REGISTER_FILE="$PACKAGE_DIR/register.py"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_FILE="$SCRIPT_DIR/register.py"

if [ ! -f "$PATCH_FILE" ]; then
    echo "❌ register.py not found next to patch.sh"
    exit 1
fi

# Backup original
cp "$REGISTER_FILE" "$REGISTER_FILE.bak.$(date +%s)"
cp "$PATCH_FILE" "$REGISTER_FILE"
echo "✅ Patched $REGISTER_FILE"
