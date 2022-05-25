import socket
import threading
import sys

IP = "localhost"
PORT = 1235
BUF_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((IP, PORT))
except ConnectionRefusedError:
    sys.stderr.write("Error,can't connect to server")
    sys.exit(1)


send = True


def handle_msg(connection: socket.socket):
    while send:
        data = connection.recv(BUF_SIZE).decode()
        print(data)


print("Waiting to server...")
confirmation = client.recv(5).decode()
if confirmation == "START":
    print("You can send messages")
    threading.Thread(target=handle_msg, args=(client,)).start()
    while send:
        msg = input()
        msg += "\n"
        if msg == "!quit":
            send = False
            client.send("")
        else:
            client.send(msg.encode())
