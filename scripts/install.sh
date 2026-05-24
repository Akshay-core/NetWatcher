#!/usr/bin/env bash
# NetWatcher — One-command setup for Linux/Mac
# Usage: bash scripts/install.sh

set -e
echo ""
echo "🛡  NetWatcher Setup"
echo "────────────────────────────────────"

# Check Python
python3 --version >/dev/null 2>&1 || { echo "✗ Python3 not found. Install Python 3.8+"; exit 1; }
echo "✓  Python found: $(python3 --version)"

# Check nmap
if command -v nmap &>/dev/null; then
    echo "✓  Nmap found: $(nmap --version | head -1)"
else
    echo "⚠  Nmap not found."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   Run: sudo apt-get install -y nmap"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   Run: brew install nmap"
    fi
    echo "   Then re-run this script."
    exit 1
fi

# Install Python deps
echo ""
echo "Installing Python dependencies…"
pip3 install -r requirements.txt --quiet

echo ""
echo "✓  NetWatcher is ready!"
echo ""
echo "  Scan local network:   python3 netwatcher.py scan --local"
echo "  Custom target:        python3 netwatcher.py scan --target 192.168.1.0/24"
echo "  View history:         python3 netwatcher.py history"
echo "  Open last report:     python3 netwatcher.py report"
echo ""
