# run_analysis.py
import pathlib
import socket
import sys
import threading
import time

import requests
import uvicorn

from backend.app import app


HOST = "127.0.0.1"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def start_server(port: int) -> uvicorn.Server:
    config = uvicorn.Config(
        app,
        host=HOST,
        port=port,
        log_level="info",
    )

    server = uvicorn.Server(config)

    thread = threading.Thread(
        target=server.run,
        daemon=True,
    )
    thread.start()

    return server


def wait_for_server(port: int, timeout_seconds: int = 30) -> None:
    health_url = f"http://{HOST}:{port}/api/health"
    deadline = time.time() + timeout_seconds
    last_error = None

    while time.time() < deadline:
        try:
            response = requests.get(health_url, timeout=1)

            if response.status_code == 200:
                return

        except requests.RequestException as error:
            last_error = error

        time.sleep(0.25)

    raise RuntimeError(
        f"Server did not start within {timeout_seconds} seconds. "
        f"Last error: {last_error}"
    )


def run_analysis(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    port: int,
) -> None:
    url = f"http://{HOST}:{port}/api/analyse"

    with input_path.open("rb") as input_file:
        response = requests.post(
            url,
            files={"file": input_file},
            timeout=300,
        )
        response.raise_for_status()

    output_path.write_bytes(response.content)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: run_analysis.exe <input_excel> <output_pdf>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1]).resolve()
    output_path = pathlib.Path(sys.argv[2]).resolve()

    if not input_path.is_file():
        print(f"Input Excel file not found: {input_path}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    port = find_free_port()
    print(f"Starting temporary local server on http://{HOST}:{port}")

    start_server(port)
    wait_for_server(port)

    print("Server ready. Running analysis...")

    try:
        run_analysis(input_path, output_path, port)
        print(f"Report written to: {output_path}")

    except requests.RequestException as error:
        print(f"Analysis request failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
