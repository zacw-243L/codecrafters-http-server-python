import socket
from typing import List


def parse_input(input: bytes) -> List[str]:
    input = input.decode()
    return input.split("\r\n")


def extract_random_string(path: str) -> str:
    return path.split("/")[-1]


def handle_request(input: bytes) -> bytes:
    input = parse_input(input)
    method, path, version = input[0].split(" ")
    random_string = extract_random_string(path)
    content_type = "text/plain"
    content_length = len(random_string.encode())
    body = random_string.encode()
    headers = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n"
    status_line = "HTTP/1.1 200 OK\r\n"
    response = f"{status_line}{headers}\r\n{body}"
    return response


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, client = server_socket.accept()

    with connection:
        input = connection.recv(1024)
        connection.sendall(handle_request(input))
    server_socket.close()


if __name__ == "__main__":
    main()
