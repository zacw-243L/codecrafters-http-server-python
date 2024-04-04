import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection = server_socket.accept()[0]  # wait for client

    request = connection.recv(4096)
    request = request.decode()
    print(request)

    path_start = request.find("/")
    path_end = request.find(" ", path_start)
    path = request[path_start:path_end]

    file_start = path.rfind("/") + 1
    file_name = path[file_start:]
    
    path = path.removesuffix(file_name)

    print(path, "\n")
    print(file_name, "\n\n")

    if path == "/":
        msg = "HTTP/1.1 200 OK\r\n\r\n"
    elif path == "/echo/":
        msg = "HTTP/1.1 200 OK\r\n"
        msg += "Content-Type: text/plain\r\n"
        msg += "Content-Length: ", len(file_name), "\r\n"
    else:
        msg = "HTTP/1.1 404 Not Found\r\n\r\n"

    connection.send(msg.encode())

    if __name__ == "__main__":
        main()
