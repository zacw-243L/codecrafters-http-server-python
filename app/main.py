import socket
import sys
import threading
from pathlib import Path

CR = "\r\n"
CR_END = CR + CR

RESPONSES = {
    "OK": f"HTTP/1.1 200 OK{CR_END}",
    "NotFound": f"HTTP/1.1 404 Not Found{CR}Content-Length: 0{CR_END}",
    "NoContent": f"HTTP/1.1 201 No Content{CR_END}",
}


def respond(content=None, content_type="text/plain"):
    response = [RESPONSES["OK"]]

    if content:
        response += [f"Content-Type: {content_type}", f"Content-Length: {len(content)}", "", f"{content}", ]
        return CR.join(response).encode()
    return RESPONSES["OK"].encode()


def handle(client_socket: socket.socket, dir: str):
    request = client_socket.recv(4096)

    lines = request.decode().split(CR)
    method, path, version = lines[0].split(" ")

    handlers = {
        "/": lambda: respond(),
        "/echo/": lambda: respond(path[6:]),
        "/user-agent": lambda: respond(lines[1][12:]),
        "/files": {
            "GET": lambda: handle_file_get(dir, path, client_socket),
            "POST": lambda: handle_file_post(dir, path, lines, client_socket),
        },
    }

    handler = handlers.get(path, handlers["/"])
    if isinstance(handler, dict):
        handler = handler.get(method, lambda: respond())

    client_socket.send(handler())
    client_socket.close()


def handle_file_get(dir, path, client_socket):
    path = Path(f"{dir}/{path[7:]}")
    if dir and path.is_file():
        file = path.read_text()
        client_socket.send(respond(file, "application/octet-stream"))
    else:
        client_socket.send(respond())


def handle_file_post(dir, path, lines, client_socket):
    sep = lines.index("")
    content = CR.join(lines[sep + 1:])
    path = Path(f"{dir}/{path[7:]}")
    with open(path, "w") as file:
        file.write(content)
    client_socket.send(respond())


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
