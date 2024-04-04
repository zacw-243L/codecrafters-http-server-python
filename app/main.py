import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))
    connection, address = server_socket.accept()  # wait for client

    with connection:
        print("Connected by", address)
        # infinite loop to keep the connection open and receive data continuously
        while True:
            data = connection.recv(1024).decode("utf-8")
            if not data:
                continue
            path = data.split()[1]
            if path and path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\nHello, World!"
            elif path and "echo" in path:
                response_data = path[len("/echo/") :]
                print(f"RESPONSE DATA: {response_data}")
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}".format(
                    len(response_data), response_data
                )
                print(f"RESPONSE: {response_data}")
            elif path and "user-agent" in path:
                user_agent = data.split("\r\n")[2]
                response_data = user_agent[len("User-Agent: ") :]
                print(f"RESPONSE DATA: {response_data}")
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}".format(
                    len(response_data), response_data
                )

                print(f"RESPONSE: {response_data}")
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
            print("Sending", response)
            connection.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
    