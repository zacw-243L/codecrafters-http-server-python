import socket
from typing import List


def parse_input(input: bytes) -> List[str]:
    input = input.decode()
    return input.split("\r\n")


def handle_request(input: bytes) -> bytes:
    # we expect requests like this:
    # GET /index.html HTTP/1.1
    # Host: localhost:4221
    # User-Agent: curl/7.64.1
    input = parse_input(input)
    method, path, version = input[0].split(" ")
    output = ""
    if path == "/":
        output = b"HTTP/1.1 200 OK\r\n\r\n"
    else:
        output = b"HTTP/1.1 404 Not Found\r\n\r\n"
    return output


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, client = server_socket.accept()  # wait for

    with connection:
        input = connection.recv(1024)
        connection.sendall(handle_request(input))
    server_socket.close()


if __name__ == "__main__":
    main()
