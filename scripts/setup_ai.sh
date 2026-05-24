#!/usr/bin/env bash
# NetWatcher AI Setup — installs Ollama and pulls the best model for your GPU
set -e

echo ""
echo "🤖  NetWatcher AI Setup"
echo "────────────────────────────────────"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓  Linux detected"
    if ! command -v ollama &>/dev/null; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "✓  Ollama already installed: $(ollama --version)"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✓  macOS detected"
    if ! command -v ollama &>/dev/null; then
        echo "→  Download Ollama from: https://ollama.ai/download"
        echo "   Then re-run this script."
        exit 1
    fi
else
    echo "Windows: Download Ollama from https://ollama.ai/download"
    echo "Then run: ollama pull mistral:7b-instruct-q4_K_M"
    exit 0
fi

# Start Ollama server in background if not running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama server..."
    ollama serve &>/dev/null &
    sleep 3
fi

echo ""
echo "Pulling AI model (mistral:7b-instruct-q4_K_M)..."
echo "This is ~4.1GB — one-time download."
echo ""
echo "  GPU requirements:"
echo "  ✓  RTX 3050 (4GB)   → mistral:7b-q4  fits perfectly"
echo "  ✓  RTX 3060 (8GB)   → llama3.1:8b-q4 also available"
echo "  ✓  CPU only         → use llama3.2:3b (slower but works)"
echo ""

# Pull best model
ollama pull mistral:7b-instruct-q4_K_M

echo ""
echo "✓  AI model ready!"
echo ""
echo "Test: python3 netwatcher.py scan --local"
echo ""
