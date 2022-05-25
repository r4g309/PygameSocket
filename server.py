import socket
import sys
import threading
import signal
from functools import partial

HOST = "localhost"
PORT = 1235
BUFF_SIZE = 1024
ROOM_SIZE = 3


def signal_handler(
    data: socket.socket,
    sig,
    frame,
):
    print("\nClosing server ")
    data.close()
    sys.exit(1)


class Room:
    def __init__(self, all_connections):
        self.all_connections = all_connections
        self.start_listen()

    def wait_data(self, connection: socket.socket):
        while True:
            data = connection.recv(BUFF_SIZE)
            if data:
                self.broadcast(data, connection)
                print(data)
            else:
                self.remove_connection(connection)
                break

    def remove_connection(self, conn):
        index = -1
        for i, values in enumerate(self.all_connections):
            connection, _ = values
            if connection == conn:
                index = i 
        if index != -1:
            self.all_connections.pop
    def broadcast(self, data, connection):
        for index, values in enumerate(self.all_connections):
            _conn, _ = values
            if _conn != connection:
                data_copy = f'{index},{data}'
                _conn.send(data_copy.encode())

    def start_listen(self):
        _conn: socket.socket
        for _conn, addr in self.all_connections:
            print(f"Wait data from {addr}")
            _conn.send(b"START")
            threading.Thread(target=self.wait_data, args=(_conn,)).start()


#TODO: Add id to connections
#TODO: in first message send if are impostor

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    signal.signal(signal.SIGINT, partial(signal_handler, server))
    temp_connections = []
    all_rooms = []
    try:
        server.bind((HOST, PORT))
    except OSError:
        sys.stderr.write("Error,ip invalid or port in use")
        sys.exit(1)
    # Server start to listen
    server.listen()
    print(f"Server started to listen in {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        temp_connections.append((conn, addr))
        if len(temp_connections) > ROOM_SIZE - 1:
            all_rooms.append(Room(temp_connections))
            temp_connections = []

    # Close connections and server
    server.close()
