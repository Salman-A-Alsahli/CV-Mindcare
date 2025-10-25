Write-Host "🚀 Setting up CV-MindCare..."
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Push-Location frontend
npm install
Pop-Location

Write-Host "✅ Setup complete! Run 'make run' to start the app." 
