import os.path
import socket  # noqa: F401
import threading
from dataclasses import dataclass
import re
import argparse
from typing import Optional
import gzip
HTTP___NOT_FOUND_ = "HTTP/1.1 404 Not Found"

ENCODING = 'utf-8'


@dataclass
class HttpResponse:
    status_line: str
    headers: dict[str, str]
    body: Optional[bytes]

@dataclass
class ServerArguments:
    file_dir: str

@dataclass
class HttpRequest:
    method: str
    path: str
    protocol: str
    host: str
    host: str
    user_agent: str
    accept: str
    body: str
    accept_encoding: Optional[str]
    close: bool


def handle_file(request_data: HttpRequest, server_args: ServerArguments) -> HttpResponse:
    file_name = request_data.path.replace("/files/", server_args.file_dir)

    if request_data.method == 'GET':
        if not os.path.isfile(file_name):
            return HttpResponse(HTTP___NOT_FOUND_, {}, None)
        size = os.path.getsize(file_name)
        with open(file_name, 'rb') as file:
            return HttpResponse("HTTP/1.1 200 OK", {"Content-Type": "application/octet-stream", "Content-Length": size}, file.read())
    if request_data.method == 'POST':
        with open(file_name, 'wb') as file:
            file.write(request_data.body.encode(ENCODING))
        return HttpResponse("HTTP/1.1 201 Created", {}, None)




def handle_echo(request_data: HttpRequest) -> HttpResponse:
    arg = re.sub("^/echo/", "", request_data.path)
    headers = {
        "Content-Type": "text/plain",
        "Content-Length": len(arg)
    }
    return HttpResponse("HTTP/1.1 200 OK", headers, arg.encode(ENCODING))

def handle_user_agent(request_dat: HttpRequest):
    return HttpResponse("HTTP/1.1 200 OK", {"Content-Type": "text/plain", "Content-Length": len(request_dat.user_agent)}, request_dat.user_agent.encode(ENCODING))

def format_http_response(response: HttpResponse) -> bytes:
    res = response.status_line.encode(ENCODING) + "\r\n".encode(ENCODING)
    for key, val in response.headers.items():
        res = res + f"{key}: {val}\r\n".encode(ENCODING)
    res = res + "\r\n".encode(ENCODING)
    if response.body:
        res = res + response.body
    return res


def handle_compression(request: HttpRequest, response: HttpResponse):
    if not request.accept_encoding:
        return
    if 'gzip' in request.accept_encoding.split(", "):
        temp_data = gzip.compress(response.body)
        response.headers['Content-Length'] = str(len(temp_data))
        response.body = temp_data
        response.headers['Content-Encoding'] = 'gzip'


def parse_http_request(data: bytes):
    parts = data.decode(ENCODING).split(' ')
    method = parts[0]
    path = parts[1]
    protocol = parts[2].split("\r\n")[0]
    more_parts = data.decode(ENCODING).split("\r\n")[1:]
    more_parts_dict = {}
    body = None
    for thingy in more_parts:
        components = thingy.split(": ")
        if ": " in thingy:
            more_parts_dict[components[0]] = components[1]
        else:
            body = components[0]
    close = True if more_parts_dict.get("Connection", "aaaaaa") == 'close' else False
    return HttpRequest(method, path, protocol, more_parts_dict.get('HOST', None), more_parts_dict.get('User-Agent', None), more_parts_dict.get('Accept', None), body, more_parts_dict.get("Accept-Encoding", None), close)

def handle_request_content(request_data: HttpRequest, server_args: ServerArguments ) -> HttpResponse:
    if request_data.path == '/':
        return HttpResponse("HTTP/1.1 200 OK", {}, None)
    if request_data.path.startswith("/echo/"):
        return handle_echo(request_data)
    if request_data.path.startswith('/files/'):
        return handle_file(request_data, server_args)
    if request_data.path == "/user-agent":
        return handle_user_agent(request_data)


    return HttpResponse(HTTP___NOT_FOUND_, {}, None)

def handle_request(conn: socket.socket, server_args: ServerArguments):
    close = False
    while not close:
        data = conn.recv(1024)
        request_data = parse_http_request(data)
        temp = handle_request_content(request_data, server_args)
        handle_compression(request_data, temp)
        close = request_data.close
        if close:
            temp.headers["Connection"] = "close"

        conn.sendall(format_http_response(temp))
        if close:
            conn.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-d', '--directory')  # option that takes a value
    args = parser.parse_args()
    server_args = ServerArguments(args.directory)

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_request, args=(conn, server_args)).start()






if __name__ == "__main__":
    main()

# Done