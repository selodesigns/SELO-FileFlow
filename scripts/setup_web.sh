#!/bin/bash

# FileFlow Web UI Setup Script
# Installs all dependencies for the web interface

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WEB_DIR="$PROJECT_ROOT/web"

echo "🔧 FileFlow Web UI Setup"
echo "========================"
echo ""

# Check Python
echo "📌 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2) found"
echo ""

# Check Node.js
echo "📌 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or later."
    exit 1
fi
echo "✅ Node.js $(node --version) found"
echo ""

# Check npm
echo "📌 Checking npm installation..."
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi
echo "✅ npm $(npm --version) found"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd "$PROJECT_ROOT"
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd "$WEB_DIR"
if [ -d "node_modules" ]; then
    echo "ℹ️  node_modules already exists, reinstalling..."
    rm -rf node_modules package-lock.json
fi
npm install
echo "✅ Node.js dependencies installed"
echo ""

echo "✨ Setup complete!"
echo ""
echo "To start the development environment, run:"
echo "  ./scripts/start_web_dev.sh"
echo ""
echo "Or start services manually:"
echo "  Terminal 1: python -m fileflow.main --web"
echo "  Terminal 2: cd web && npm run dev"
echo ""
