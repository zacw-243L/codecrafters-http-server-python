# Uncomment this to pass the first stage
import socket

HOST = "localhost"
PORT = 4221

print(f"Server started at: http://{HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)

            if not data:
                break

            conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
            conn.sendall(data)
