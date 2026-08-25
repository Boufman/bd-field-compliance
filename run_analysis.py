import pathlib
import sys
import threading
import time

import requests
import uvicorn

from backend.app import app

PORT = 8000
HOST = "127.0.0.1"


def start_server():
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )

    server = uvicorn.Server(config)

    thread = threading.Thread(
        target=server.run,
        daemon=True,
    )
    thread.start()

    for _ in range(30):
        try:
            response = requests.get(
                f"http://{HOST}:{PORT}/api/health",
                timeout=1,
            )
            if response.status_code == 200:
                return server, thread
        except requests.RequestException:
            time.sleep(0.5)

    server.should_exit = True
    thread.join(timeout=5)
    raise RuntimeError("The local analysis server did not start.")


def run_analysis(input_path: pathlib.Path, output_path: pathlib.Path):
    url = f"http://{HOST}:{PORT}/api/analyse"

    with input_path.open("rb") as file_handle:
        response = requests.post(
            url,
            files={"file": file_handle},
            timeout=300,
        )

    response.raise_for_status()
    output_path.write_bytes(response.content)


def main():
    if len(sys.argv) != 3:
        print("Usage: BD_Analysis_Tool.exe <input_excel> <output_pdf>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    output_path = pathlib.Path(sys.argv[2]).expanduser().resolve()

    if not input_path.is_file():
        print(f"Input Excel file not found: {input_path}")
        sys.exit(1)

    server, server_thread = start_server()

    try:
        run_analysis(input_path, output_path)
        print(f"Report written to: {output_path}")
    finally:
        server.should_exit = True
        server_thread.join(timeout=10)


if __name__ == "__main__":
    main()
