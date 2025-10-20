import webbrowser
import multiprocessing
import time
from pathlib import Path

def _start_uvicorn():
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    p = multiprocessing.Process(target=_start_uvicorn, daemon=True)
    p.start()
    # give server a second to start
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/")
    try:
        while p.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        p.terminate()
