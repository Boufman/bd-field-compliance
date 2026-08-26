# run_analysis.py
import subprocess
import sys
import time
import pathlib
import requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
BACKEND_MODULE = 'backend.app'  # adjust if needed
PORT = 8000
HOST = "127.0.0.1"

def start_server():
    proc = subprocess.Popen(
        ["uvicorn", "backend.app:app", "--port", "8000"],
        cwd=str(BASE_DIR),
    )
    time.sleep(3)
    return proc

def run_analysis(input_path: pathlib.Path, output_path: pathlib.Path):
    url = f"http://{HOST}:{PORT}/api/analyse"
    with input_path.open("rb") as f:
        files = {"file": f}
        resp = requests.post(url, files=files)
        resp.raise_for_status()
    output_path.write_bytes(resp.content)

def main():
    if len(sys.argv) != 3:
        print("Usage: run_analysis.exe <input_excel> <output_pdf>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1]).resolve()
    output_path = pathlib.Path(sys.argv[2]).resolve()

    server_proc = start_server()
    try:
        run_analysis(input_path, output_path)
        print(f"Report written to: {output_path}")
    finally:
        server_proc.terminate()
        server_proc.wait()

if __name__ == "__main__":
    main()