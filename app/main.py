import socket


def main():

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()

    with connection:
        print("Connected by", address)
        # infinite loop to keep the connection open and receive data continuously
        while True:
            request = connection.recv(1024)
            req_str = request.decode("utf-8")
            splits = req_str.split(" ")
            method = splits[0]
            path = splits[1]

            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8")

            if path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n".encode("utf-8")
            elif "/echo/" in path:
                data = path.split("/echo/")[1]
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(data)}\r\n\r\n{data}".encode("utf-8")

            connection.sendall(response)

            
if __name__ == "__main__":
    main()

