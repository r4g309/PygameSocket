import signal
import socket
import sys
import threading
from functools import partial
from json import dumps, loads
from random import choice

HOST = "172.30.16.199"
PORT = 1235
BUFF_SIZE = 1024
ROOM_SIZE = 2


def signal_handler(
    server: socket.socket,
    sig,
    frame,
):
    print("\nClosing server ")
    server.close()
    sys.exit(1)


class Room:
    def __init__(self, all_connections):
        self.all_connections = all_connections
        self.start_listen()

    def wait_data(self, connection: socket.socket):
        while True:
            try:
                data = connection.recv(BUFF_SIZE)
            except ConnectionResetError:
                self.remove_connection(connection)
                connection.close()
                break
            if data == b"DISCONNECT":
                connection.send(b"bye")
                self.remove_connection(connection)
                connection.close()
                break
            if data:
                self.broadcast(data, connection)

    def remove_connection(self, conn):
        index = -1
        for i, values in enumerate(self.all_connections):
            connection, _ = values
            if connection == conn:
                index = i
        if index != -1:
            self.all_connections.pop(index)

    def broadcast(self, data, connection):
        for _conn, _ in self.all_connections:
            if _conn != connection:
                try:
                    _conn.send(data)
                except ConnectionAbortedError:
                    self.remove_connection(_conn)

    def start_listen(self):
        _conn: socket.socket
        impostor = choice(self.all_connections)
        id_impostor = self.all_connections.index(impostor)
        impostor, _ = impostor
        for index, (_conn, addr) in enumerate(self.all_connections):
            is_killer = _conn == impostor
            print(f"Wait data from {addr}")
            _conn.send(
                bytes(
                    dumps(
                        {
                            "id": index,
                            "room_size": ROOM_SIZE,
                            "killer": is_killer,
                            "id_killer": id_impostor,
                        }
                    ),
                    encoding="utf-8",
                )
            )
            threading.Thread(target=self.wait_data, args=(_conn,)).start()


# TODO: in first message send if are impostor

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
