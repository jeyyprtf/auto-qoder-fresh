#!/bin/bash
set -e

echo "============================================"
echo "  QODER AUTO-REGIST FRESH - Installation"
echo "============================================"
echo ""

echo "1️⃣  Installing qoder-autopilot (force install from git)..."
pip install --force-reinstall "qoder-autopilot @ git+https://github.com/Daivageralda/qoder-autopilot.git"

echo "2️⃣  Installing Python dependencies..."
pip install pydantic>=2.0 python-dotenv>=1.0 requests>=2.28 faker>=20.0 playwright>=1.40 openai>=1.0 opencv-python-headless>=4.8 --quiet

echo "3️⃣  Installing qoder-cli (npm)..."
npm i -g @qoder-ai/qodercli --quiet

echo "4️⃣  Installing Playwright browsers..."
playwright install chromium --with-deps || {
    echo "⚠️  Chromium not supported, trying Firefox fallback..."
    playwright install firefox --with-deps || echo "⚠️  Browsers may fail on unsupported OS"
}

echo "5️⃣  Checking configuration..."
if [ ! -f config.json ]; then
    echo "   Creating default config.json..."
    cat > config.json << 'CONF'
{
  "worker_url": "https://mail-api.jujukaizen.web.id",
  "worker_domain": "jujukaizen.web.id"
}
CONF
fi

echo "6️⃣  Testing installation..."
pip show qoder-autopilot | head -3
qoder-autopilot doctor 2>&1 | tail -5

echo ""
echo "============================================"
echo "  ✅ Installation Complete!"
echo "============================================"
echo ""
echo "You can now run:"
echo "  ./fresh-claim-v2.py"
echo ""
echo "Or register one account manually:"
echo "  qoder-autopilot --manual-captcha -n 1"
echo ""
