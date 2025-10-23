#!/bin/bash

# FileFlow Web Development Launcher
# Starts both the API server and the frontend development server

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WEB_DIR="$PROJECT_ROOT/web"

echo "🚀 Starting FileFlow Web Development Environment"
echo "================================================"

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not found. Installing Python dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Check if Node dependencies are installed
echo "📦 Checking Node.js dependencies..."
if [ ! -d "$WEB_DIR/node_modules" ]; then
    echo "❌ Node modules not found. Installing..."
    cd "$WEB_DIR"
    npm install
    cd "$PROJECT_ROOT"
fi

echo ""
echo "✅ Dependencies ready"
echo ""
echo "Starting services..."
echo "  • API Server: http://localhost:9001"
echo "  • Web UI: http://localhost:5173"
echo "  • API Docs: http://localhost:9001/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API server in background
cd "$PROJECT_ROOT"
python -m fileflow.main --web --host 127.0.0.1 --port 9001 &
API_PID=$!

# Give the API server time to start
sleep 2

# Start frontend dev server in background
cd "$WEB_DIR"
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait
