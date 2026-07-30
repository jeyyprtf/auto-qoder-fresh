#!/bin/bash
set -e
echo "Installing qoder-autopilot + dependencies..."
pip install "qoder-autopilot @ git+https://github.com/Daivageralda/qoder-autopilot.git" -r requirements.txt

echo "Installing playwright browsers..."
playwright install firefox --with-deps

echo ""
echo "✅ Done! You can now run:"
echo "./fresh-claim-v2.py"
