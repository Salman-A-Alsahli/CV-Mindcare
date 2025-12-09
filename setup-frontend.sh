#!/bin/bash

# CV-Mindcare Frontend Setup Script
# This script installs all necessary dependencies for the web dashboard

set -e

echo "========================================="
echo "CV-Mindcare Frontend Setup"
echo "========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "📦 Installing frontend dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the dashboard:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Or use the start-dashboard.sh script to start both backend and frontend"
echo ""
