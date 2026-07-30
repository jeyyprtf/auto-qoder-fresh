#!/bin/bash
set -e

echo "============================================"
echo "  QODER AUTO-REGIST FRESH - Installation"
echo "============================================"
echo ""

echo "1️⃣  Installing qoder-autopilot from MAIN branch..."
pip uninstall -y qoder-autopilot 2>/dev/null || true
pip install --force-reinstall "qoder-autopilot @ git+https://github.com/Daivageralda/qoder-autopilot.git@main"

echo "2️⃣  Installing Python dependencies..."
pip install pydantic>=2.0 python-dotenv>=1.0 requests>=2.28 faker>=20.0 playwright>=1.40 openai>=1.0 opencv-python-headless>=4.8 --quiet

echo "3️⃣  Installing qoder-cli (npm)..."
npm i -g @qoder-ai/qodercli 2>/dev/null || true

echo "4️⃣  Installing Playwright browsers..."
playwright install chromium --with-deps 2>/dev/null || playwright install firefox --with-deps 2>/dev/null || echo "⚠️ Browser may fail on unsupported OS"

echo "5️⃣  Checking configuration..."
if [ ! -f config.json ]; then
    cat > config.json << 'CONF'
{
  "worker_url": "https://mail-api.jujukaizen.web.id",
  "worker_domain": "jujukaizen.web.id"
}
CONF
fi

echo "6️⃣  Testing installation..."
pip show qoder-autopilot | head -2

echo ""
echo "============================================"
echo "  ✅ Installation Complete!"
echo "============================================"
echo ""
echo "Now run:"
echo "  ./fresh-claim-v2.py"
