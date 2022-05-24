import socket
import sys
import threading

HEIGTH,WIDTH = 300,300
FPS = 60
SIZE = 30
SPEED = 10
IP = "localhost"
PORT = 1237

all_connections = []

def broadcast(data,connection):
    for conn in all_connections:
        if conn != connection:
            conn.send(data)

def handle_connection(conn:socket.socket,addr):
    all_connections.append(conn)
    while True:
        data = conn.recv(1024)
        if data:
            broadcast(data,conn)
            print(addr,data)
        else:
            break

if __name__ == "__main__":
    print("Server started")
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.bind((IP,PORT))
    client.listen()
    while True:
        try:
  
            conn,addr = client.accept()
            client_th = threading.Thread(target=handle_connection,args=(conn,addr))
            client_th.start()
        except ConnectionRefusedError:
            print("Error, can't not connect")
            sys.exit(1)
