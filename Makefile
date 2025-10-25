# Makefile for CV-MindCare

setup:
	@echo "🔧 Installing dependencies..."
	python -m venv venv
	. venv/Scripts/activate && pip install -r requirements.txt
	cd frontend && npm install

run:
	@echo "🚀 Starting backend + frontend..."
	( . venv/Scripts/activate && uvicorn run_app:app --reload ) & \
	cd frontend && npm run dev

build:
	@echo "📦 Building production frontend..."
	cd frontend && npm run build

serve:
	@echo "🌐 Serving built frontend via backend..."
	. venv/Scripts/activate && uvicorn run_app:app --reload

clean:
	@echo "🧹 Cleaning up..."
	rmdir /s /q venv || true
	rmdir /s /q frontend\\node_modules || true
	rmdir /s /q frontend\\dist || true
