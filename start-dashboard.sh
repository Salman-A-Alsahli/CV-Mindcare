#!/bin/bash

# CV-Mindcare Dashboard Launcher
# This script starts both the FastAPI backend and React frontend

set -e

echo "========================================="
echo "CV-Mindcare Dashboard Launcher"
echo "========================================="
echo ""

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    echo "ℹ️  Detected ARM64 architecture ($ARCH)"
    
    # Check if node_modules exists and has the Rollup module
    if [ ! -d "$(dirname "$0")/frontend/node_modules" ]; then
        echo ""
        echo "⚠️  Frontend dependencies not installed!"
        echo "🔧 Please run: ./setup-frontend.sh"
        echo ""
        exit 1
    fi
    
    # Check specifically for Rollup ARM64 module
    if [ ! -d "$(dirname "$0")/frontend/node_modules/@rollup/rollup-linux-arm64-gnu" ] && \
       [ ! -f "$(dirname "$0")/frontend/node_modules/rollup/dist/native.js" ]; then
        echo ""
        echo "⚠️  Rollup ARM64 module not found!"
        echo "🔧 This is a known issue on ARM64 platforms."
        echo ""
        echo "To fix this, run:"
        echo "  cd frontend"
        echo "  rm -rf node_modules package-lock.json"
        echo "  npm install --legacy-peer-deps --force"
        echo ""
        echo "Or simply run: ./setup-frontend.sh"
        echo ""
        exit 1
    fi
fi

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✓ Backend is already running on port 8000"
else
    echo "🚀 Starting FastAPI backend..."
    cd "$(dirname "$0")"
    python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
    sleep 3
fi

# Start frontend
echo "🚀 Starting React frontend..."
cd "$(dirname "$0")/frontend"

# Define error handler function before setting trap
handle_error() {
    echo ""
    echo "❌ Frontend failed to start!"
    echo ""
    if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        echo "This appears to be a Rollup module error on ARM64."
        echo ""
        echo "To fix this:"
        echo "  1. cd frontend"
        echo "  2. rm -rf node_modules package-lock.json"
        echo "  3. npm install --legacy-peer-deps --force"
        echo ""
        echo "Or run: ./setup-frontend.sh"
        echo ""
    else
        echo "Try running: ./setup-frontend.sh"
        echo ""
    fi
    
    # Cleanup backend if we started it
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 1
}

# Set trap to catch errors and provide helpful message
trap 'handle_error' ERR

npm run dev &
FRONTEND_PID=$!

# Remove trap after successful start
trap - ERR

echo ""
echo "✅ Dashboard is starting!"
echo ""
echo "📊 Backend API:  http://localhost:8000"
echo "🌐 Dashboard:    http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $FRONTEND_PID

# Cleanup
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
fi
