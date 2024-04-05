import socket
import sys
import threading
from pathlib import Path

CR = "\r\n"
CR_END = CR + CR


def respond_OK(content=None, content_type="text/plain"):
    response = ["HTTP/1.1 200 OK"]

    if content:
        response += [f"Content-Type: {content_type}", f"Content-Length: {len(content)}", "", f"{content}", ]
        return CR.join(response).encode()
    return (response[0] + CR_END).encode()


def respond_NotFound():
    return f"HTTP/1.1 404 Not Found{CR}Content-Length: 0{CR_END}".encode()


def respond_NoContent():
    return f"HTTP/1.1 201 No Content{CR_END}".encode()


def handle(client_socket: socket.socket, dir: str):
    request = client_socket.recv(4096)

    lines = request.decode().split(CR)
    method, path, version = lines[0].split(" ")

    if path == "/":
        client_socket.send(respond_OK())

    elif path.startswith("/echo/"):
        rand_str = path[6:]
        client_socket.send(respond_OK(rand_str))

    elif path == "/user-agent":
        user_agent = ""
        for header in lines[1:]:
            if header.startswith("User-Agent"):
                user_agent = header[12:]
        client_socket.send(respond_OK(user_agent))

    elif path.startswith("/files"):
        filename = path[7:]
        path = Path(f"{dir}/{filename}")

        if method == "GET":
            if dir and path.is_file():
                file = path.read_text()
                client_socket.send(respond_OK(file, "application/octet-stream"))
            else:
                client_socket.send(respond_NotFound())
        elif method == "POST":
            sep = lines.index("")
            content = CR.join(lines[sep + 1:])
            with open(path, "w") as file:
                file.write(content)
            client_socket.send(respond_NoContent())

    else:
        client_socket.send(respond_NotFound())

    client_socket.close()


def main(dir=None):
    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("localhost", 4221))
        server_socket.listen()

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle, args=(client_socket, dir,), daemon=True, ).start()


if __name__ == "__main__":
    args = sys.argv

    dir = None
    for i in range(len(args)):
        if args[i] == "--directory":
            dir = args[i + 1]

    main(dir)
