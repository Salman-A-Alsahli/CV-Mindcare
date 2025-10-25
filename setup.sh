#!/usr/bin/env bash
set -e
echo "🚀 Setting up CV-MindCare..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..

echo "✅ Setup complete! Run 'make run' to start the app."
