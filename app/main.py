from sys import argv
import socket
import threading


def handle_request(conn, addr):
    data = conn.recv(1024).decode("utf-8")
    request = data.split("\r\n")
    method = request[0].split(" ")[0]
    path = request[0].split(" ")[1]
    body = request[-1]
    user_agent = ""
    accept_encoding = ""
    for line in request:
        if line.startswith("User-Agent:"):
            user_agent = line[len("User-Agent: ") :]
        if line.startswith("Accept-Encoding:"):
            accept_encoding = line[len("Accept-Encoding: ") :]

    encoding = ""
    if "gzip" in accept_encoding:
        encoding = "Content-Encoding: gzip\r\n"
    if path == "/":
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
    elif path == "/user-agent":
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}\r\n"
        conn.send(response.encode())
    elif "/files" in path:
        if method == "POST":
            directory = argv[2]
            filename = path[7:]
            try:
                with open(f"/{directory}/{filename}", "w") as f:
                    f.write(f"{body}")
                response = f"HTTP/1.1 201 Created\r\n\r\n"
            except Exception as e:
                response = f"HTTP/1.1 404 Not Found\r\n\r\n"
            conn.send(response.encode())
        elif method == "GET":
            f_name = path.split("/")[-1]
            try:
                with open(argv[2] + f_name) as f:
                    content = f.read()
                    cont_length = len(content)
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {str(cont_length)}\r\n\r\n{content}"
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
            conn.send(response.encode())
    elif path.startswith("/echo"):
        random_path = path[6:]
        response = f"HTTP/1.1 200 OK\r\n{encoding}Content-Type: text/plain\r\nContent-Length: {len(random_path)}\r\n\r\n{random_path}\r\n"
        conn.send(response.encode())
    else:
        conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    conn.close()


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, addr = server_socket.accept()  # wait for client
        threading.Thread(target=handle_request, args=(conn, addr)).start()


if __name__ == "__main__":
    main()