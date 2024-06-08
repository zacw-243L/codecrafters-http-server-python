import os
import socket

# Will need this to access command line arguments.
import sys
from threading import Thread

"""
run ./your_server.sh in one terminal session, and nc -vz 127.0.0.1 4221 in another.
"""

accepted_encoding_types = ["gzip", ]


def request_handler(conn):
    if len(sys.argv) == 3:
        directory_location = sys.argv[-1]
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            request_data = data.decode().split("\r\n")
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            request_type, request_path = request_data[0].split(" ", 1)
            encoding_type = request_data[2].split(": ")[-1]
            request_path = request_path.split(" ")[0]

            if request_type == "POST" and "/files/" in request_path:
                file_name = request_path.split("/")[-1]
                file_save_location = f"{directory_location}{file_name}"
                request_file_contents = request_data[-1]
                with open(file_save_location, "w") as new_file:
                    new_file.write(request_file_contents)
                response = b"HTTP/1.1 201 Created\r\n\r\n"

            if request_type == "GET":
                if request_path == "/":
                    response = b"HTTP/1.1 200 OK\r\n\r\n"

                elif "echo" in request_path:
                    echo_val = request_path.split("/")[-1]
                    if encoding_type in accepted_encoding_types:
                        response = f"HTTP/1.1 200 OK\r\nContent-Encoding:{encoding_type}\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_val)}\r\n\r\n{echo_val}".encode()
                    else:
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_val)}\r\n\r\n{echo_val}".encode()
                elif "user-agent" in request_path:
                    user_agent_header_data = request_data[2].split(" ")[1]
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent_header_data)}\r\n\r\n{user_agent_header_data}".encode()
                elif "/files/" in request_path:
                    file_name = request_path.split("/")[-1]
                    if os.path.exists(f"{directory_location}{file_name}"):
                        with open(f"{directory_location}{file_name}") as f:
                            file_contents = f.read()
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_contents)}\r\n\r\n{file_contents}".encode()
            conn.sendall(response)


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, _ = server_socket.accept()
        Thread(target=request_handler, args=(conn,)).start()


if __name__ == "__main__":
    main()