import socket
import threading

HTTP_SUCCESS_RESPONSE = "HTTP/1.1 200 OK\r\n"
HTTP_NOT_FOUND_RESPONSE = "HTTP/1.1 404 NOT-FOUND\r\n\r\n"


def formatResponse(request_params):
    response = []
    for param in range(2, len(request_params)):
        response.append(request_params[param])

        if param != len(request_params) - 1:
            response.append("/")
    return "".join(response)


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection = server_socket.accept()
        thread_connection = threading.Thread(target=handler, args=(connection,), daemon=True).start()


def handler(connection):
    data = connection[0].recv(1024)
    request = data.decode()

    request_lines = request.split("\r\n")
    method, route, http_version = request_lines[0].split()
    host = request_lines[1].split()

    request_params = route.split("/")

    if request_params[1] == "echo":
        body = formatResponse(request_params)
        response = (HTTP_SUCCESS_RESPONSE + "Content-Type: text/plain\r\nContent-Length: " + str(len(body)) + "\r\n\r\n" + body)
        connection[0].send(response.encode())

        if request_params[1] == "user-agent":
            user_agent = request_lines[2].split()[1]
            body = formatResponse(request_params)
            response = (
                    HTTP_SUCCESS_RESPONSE
                    + "Content-Type: text/plain\r\nContent-Length: "
                    + str(len(user_agent))
                    + "\r\n\r\n"
                    + str(user_agent)
            )
            print(response)
            connection[0].send(response.encode())

        if route != "/":
            connection[0].send(HTTP_NOT_FOUND_RESPONSE.encode())

        else:
            response = HTTP_SUCCESS_RESPONSE + "\r\n"
            connection[0].send(response.encode())
        connection[0].close()


if __name__ == "__main__":
    main()
