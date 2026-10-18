import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 4444))
s.listen(1)
print("Listening on 4444...")
conn, addr = s.accept()
print(f"Connected from {addr}")
while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Received:", data.decode())
    conn.send(b"ACK\n")
conn.close()
