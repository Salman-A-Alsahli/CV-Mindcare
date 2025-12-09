#!/bin/bash

# CV-Mindcare Dashboard Launcher
# This script starts both the FastAPI backend and React frontend

set -e

echo "========================================="
echo "CV-Mindcare Dashboard Launcher"
echo "========================================="
echo ""

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
npm run dev &
FRONTEND_PID=$!

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
