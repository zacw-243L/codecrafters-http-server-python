import socket
import os
def get_text_plain_ok_response(text, extra_headers=None):
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        f"Content-Length: {len(text)}\r\n"
    )
    if extra_headers:
        response += (
            "\r\n".join([f"{key}: {value}" for key, value in extra_headers.items()])
            + "\r\n"
        )
    response += f"\r\n{text}"
    return response
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221))
    # Read the flag --directory from the command line if it exists
    directory_value = None
    if "--directory" in os.sys.argv:
        directory_value = os.sys.argv[os.sys.argv.index("--directory") + 1]
    print(f"Directory value: {directory_value}")
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")
        data = client_socket.recv(1024).decode("utf-8")
        # Obtain the request line
        request_line = data.split("\r\n")[0]
        method = request_line.split(" ")[0]
        path = request_line.split(" ")[1]
        # Obtain the headers
        headers = data.split("\r\n")[1:-2]
        headers_dict = {
            header.split(": ")[0].lower(): header.split(": ")[1]
            for header in headers
            if header
        }
        # Obtain the body
        body = data.split("\r\n")[-1]
        print(f"Request line: {request_line}")
        print(f"Method: {method}")
        print(f"Path: {path}")
        print(f"Headers: {headers}")
        print(f"Headers dict: {headers_dict}")
        print(f"Body: {body}")
        print(f"Data: {data}")
        # Default response is 404
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        encode_response = True
        # Check diferent paths
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            # Send a response
            response_data = path.split("/echo/")[1]
            # Check if there is an Accept-Encoding header
            extra_headers = None

            if "gzip" in headers_dict.get("accept-encoding", "").lower().split(", "):
                extra_headers = {"Content-Encoding": "gzip"}
            response = get_text_plain_ok_response(
                response_data, extra_headers=extra_headers
            )
            elif path.startswith("/user-agent"):
            response_data = headers_dict.get("user-agent", "")
            response = get_text_plain_ok_response(response_data)
        elif path.startswith("/files/") and method == "GET":
            file_route = os.path.join(directory_value, path.split("/files/")[1])
            print("File route:", file_route)
            if os.path.exists(file_route):
                print("File exists")
                file_bytes = open(file_route, "rb").read()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(file_bytes)}\r\n"
                    "\r\n"
                ).encode()
                response += file_bytes
                encode_response = False
        elif path.startswith("/files/") and method == "POST":
            file_route = os.path.join(directory_value, path.split("/files/")[1])
            print("File route:", file_route)
            file_bytes = body.encode()
            with open(file_route, "wb") as file:
                file.write(file_bytes)
            response = "HTTP/1.1 201 Created\r\n\r\n"
        print(f"Response: {response}")
        client_socket.sendall(response.encode() if encode_response else response)
        client_socket.close()
        # Close the loop after one request
        # break
    if __name__ == "__main__":
        main()