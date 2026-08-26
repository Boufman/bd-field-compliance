# run_analysis.py
import subprocess
import sys
import time
import pathlib
import socket
import requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
HOST = "127.0.0.1"

def find_free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def start_server(port: int) -> subprocess.Popen:
    # Equivalent to: uvicorn backend.app:app --host 127.0.0.1 --port <port>
    proc = subprocess.Popen(
        ["uvicorn", "backend.app:app", "--host", HOST, "--port", str(port)],
        cwd=str(BASE_DIR),
    )
    # Give the server a moment to start; you can make this more robust with a health check loop.
    time.sleep(3)
    return proc

def run_analysis(input_path: pathlib.Path, output_path: pathlib.Path, port: int):
    url = f"http://{HOST}:{port}/api/analyse"
    with input_path.open("rb") as f:
        files = {"file": f}
        resp = requests.post(url, files=files)
        resp.raise_for_status()
    output_path.write_bytes(resp.content)

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_analysis.py <input_excel> <output_pdf>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1]).resolve()
    output_path = pathlib.Path(sys.argv[2]).resolve()

    port = find_free_port()
    print(f"Starting server on http://{HOST}:{port}")

    server_proc = start_server(port)
    try:
        run_analysis(input_path, output_path, port)
        print(f"Report written to: {output_path}")
    finally:
        server_proc.terminate()
        server_proc.wait()

if __name__ == "__main__":
    main()
