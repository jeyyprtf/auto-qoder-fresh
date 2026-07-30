#!/bin/bash
set -e

echo "============================================"
echo "  CLEUNINSTALL + FRESH INSTALL v2"
echo "============================================"
echo ""

# 1. Uninstall semua package terkait
echo "🧹 Cleaning Python packages..."
pip uninstall -y qoder-autopilot camoufox playwright openai requests faker pydantic python-dotenv 2>/dev/null || true

# 2. Clear pip cache
echo "🗑️  Clearing pip cache..."
rm -rf ~/.cache/pip/wheels/*.whl
rm -rf /tmp/pip-install-* /tmp/pip-ephem-wheel-cache*

# 3. Install qoder-autopilot dari MAIN branch dengan force
echo "📦 Installing qoder-autopilot from MAIN branch (fresh)..."
pip install --no-cache-dir --force-reinstall "qoder-autopilot @ git+https://github.com/Daivageralda/qoder-autopilot.git@main"

# 4. Install dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir pydantic>=2.0 python-dotenv>=1.0 requests>=2.28 faker>=20.0 playwright>=1.40 openai>=1.0 opencv-python-headless>=4.8

# 5. Install qoder-cli npm
echo "📦 Installing qoder-cli..."
npm i -g @qoder-ai/qodercli 2>/dev/null || echo "⚠️  npm skip (already installed)"

# 6. Install Playwright browser fallback
echo "📦 Installing browsers (fallback if OS unsupported)..."
playwright install chromium --with-deps 2>/dev/null || {
    playwright install firefox --with-deps 2>/dev/null || echo "⚠️  Browsers failed (VPS limitation)"
}

# 7. Create config.json jika belum ada
if [ ! -f config.json ]; then
    cat > config.json << 'CONF'
{
  "worker_url": "https://mail-api.jujukaizen.web.id",
  "worker_domain": "jujukaizen.web.id"
}
CONF
fi

# 8. Verify installation
echo ""
echo "✅ Verifying installation..."
echo "qoder-autopilot version:"
pip show qoder-autopilot | grep Version

echo ""
echo "Supported flags:"
qoder-autopilot --help 2>&1 | grep -A2 "options:" || echo "⚠️  Help unavailable"

echo ""
echo "============================================"
echo "  ✅ Fresh install complete!"
echo "============================================"
echo ""
echo "Now run: ./fresh-claim-v2.py"
echo "Or: qoder-autopilot --manual-captcha -n 1"
