import webbrowser
import multiprocessing
import time
from pathlib import Path
from fastapi import FastAPI

# Import backend app and expose a top-level `app` for uvicorn to target.
try:
    from backend.main import app as backend_app
except Exception:
    backend_app = None

app = FastAPI()
if backend_app is not None:
    # Mount the backend FastAPI application under the root
    app.mount("/", backend_app)


def _start_uvicorn():
    import uvicorn
    # when run in dev, point to backend.main which contains endpoints
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    p = multiprocessing.Process(target=_start_uvicorn, daemon=True)
    p.start()
    # If a frontend dev server is available, try to run it for nicer DX
    frontend = Path(__file__).resolve().parents[0] / 'frontend'
    npm_dev = frontend / 'node_modules'
    if npm_dev.exists():
        # assume developer has run `npm install` and can run vite
        import subprocess
        dev = subprocess.Popen(['npm', 'run', 'dev'], cwd=str(frontend))
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:3000/")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            dev.terminate()
    else:
        # serve via backend static route
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8000/")
        try:
            while p.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            p.terminate()
