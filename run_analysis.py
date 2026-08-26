import pathlib
import socket
import sys
import threading
import time

import requests
import uvicorn

from backend.app import app

HOST = "127.0.0.1"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def start_server():
    port = find_free_port()

    config = uvicorn.Config(
        app,
        host=HOST,
        port=port,
        log_level="info",
    )

    server = uvicorn.Server(config)

    server_thread = threading.Thread(
        target=server.run,
        daemon=True,
    )
    server_thread.start()

    for _ in range(30):
        try:
            response = requests.get(
                f"http://{HOST}:{port}/api/health",
                timeout=1,
            )
            if response.status_code == 200:
                return server, server_thread, port
        except requests.RequestException:
            time.sleep(0.5)

    server.should_exit = True
    server_thread.join(timeout=5)
    raise RuntimeError("The local analysis server did not start.")


def run_analysis(input_path, output_path, port):
    with input_path.open("rb") as excel_file:
        response = requests.post(
            f"http://{HOST}:{port}/api/analyse",
            files={"file": excel_file},
            timeout=300,
        )

    response.raise_for_status()
    output_path.write_bytes(response.content)


def main():
    if len(sys.argv) != 3:
        print("Usage: BD_Analysis_Tool.exe <input_excel.xlsx> <output_report.pdf>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    output_path = pathlib.Path(sys.argv[2]).expanduser().resolve()

    if not input_path.is_file():
        print(f"ERROR: Input Excel file not found: {input_path}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    server = None
    server_thread = None

    try:
        server, server_thread, port = start_server()
        print(f"Analysis server started on port {port}")

        run_analysis(input_path, output_path, port)

        print(f"Report written to: {output_path}")

    finally:
        if server is not None:
            server.should_exit = True
        if server_thread is not None:
            server_thread.join(timeout=10)


if __name__ == "__main__":
    main()
