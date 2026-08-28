import socket
import webbrowser
import uvicorn

def find_free_port(start=8000, tries=30):
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"Running at {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run("backend.app:app", host="127.0.0.1", port=port, reload=False)
