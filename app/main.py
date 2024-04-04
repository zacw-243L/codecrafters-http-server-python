import socket
from threading import Thread


def get_user_agent(request):
    lines = request.split("\r\n")
    for line in lines:
        if "User-Agent" in line:
            return line.split("User-Agent: ")[1]
    return "User-Agent not found"


def get_host(request):
    lines = request.split("\r\n")
    for line in lines:
        if "Host" in line:
            return line.split("Host: ")[1]
    return "Host not found"


def get_req(request):
    lines = request.split("\r\n")
    method, path, protocol = lines[0].split(" ")
    return method, path, protocol


def handle_connection(connection, address):
    with connection:
        print("Connected by", address)
        # infinite loop to keep the connection open and receive data continuously
        while True:
            request = connection.recv(1024)
            req_str = request.decode("utf-8")
            method, path, protocol = get_req(req_str)
            host = get_host(req_str)
            agent = get_user_agent(req_str)
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8")
            if path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n".encode("utf-8")
            elif "/user-agent" in path:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(agent)}\r\n\r\n{agent}".encode(
                    "utf-8"
                )
            elif "/echo/" in path:
                data = path.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}".encode(
                    "utf-8"
                )

            connection.sendall(response)


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        connection, address = server_socket.accept()
        thread = Thread(target=handle_connection, args=(connection, address))
        thread.start()


if __name__ == "__main__":
    main()
    