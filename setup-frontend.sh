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

# Detect architecture
ARCH=$(uname -m)
echo "✓ Architecture: $ARCH"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# ARM64 specific handling for Rollup optional dependencies
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    echo "🔧 Detected ARM64 architecture - applying workarounds..."
    echo ""
    
    # Clean up any previous failed installations
    if [ -d "node_modules" ]; then
        echo "🧹 Cleaning previous installation..."
        rm -rf node_modules
    fi
    
    if [ -f "package-lock.json" ]; then
        echo "🧹 Removing package-lock.json..."
        rm -f package-lock.json
    fi
    
    echo ""
    echo "📦 Installing frontend dependencies (ARM64 mode)..."
    # Force clean install with legacy peer deps to avoid optional dependency issues
    npm install --legacy-peer-deps --force
    
    # Verify Rollup ARM64 module is present
    ROLLUP_ARM64_FILE="node_modules/@rollup/rollup-linux-arm64-gnu/rollup.linux-arm64-gnu.node"
    ROLLUP_ARM64_DIR="node_modules/@rollup/rollup-linux-arm64-gnu"
    
    if [ ! -f "$ROLLUP_ARM64_FILE" ] && [ ! -d "$ROLLUP_ARM64_DIR" ]; then
        echo ""
        echo "⚠️  Warning: Rollup ARM64 module may not be installed correctly."
        echo "🔧 Attempting manual installation..."
        npm install @rollup/rollup-linux-arm64-gnu --save-optional --force
    fi
else
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the dashboard:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Or use the start-dashboard.sh script to start both backend and frontend"
echo ""
