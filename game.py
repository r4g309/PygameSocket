import signal
import socket
import sys
import threading
from functools import partial
from math import sqrt
from random import randint
from xml.sax.handler import all_properties

import pygame

HEIGTH, WIDTH = 300, 300
FPS = 60
SIZE = 10
SPEED = 10
IP = "localhost"
PORT = 1235
RUN = True


def signal_handler(
    client: socket.socket,
    sig,
    frame,
):
    print("\nClosing server ")
    client.close()
    sys.exit(1)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((SIZE, SIZE))
        self.surf.fill([randint(0, 255) for _ in range(3)])
        self.rect = self.surf.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGTH // 2

    def move(self, client, id_client):
        pressed_keys = pygame.key.get_pressed()
        if pygame.KEYDOWN:
            send = False
            x, y = 0, 0
            if (
                pressed_keys[pygame.K_LEFT]
                or pressed_keys[pygame.K_RIGHT]
                or pressed_keys[pygame.K_UP]
                or pressed_keys[pygame.K_DOWN]
            ):
                send = True
            if pressed_keys[pygame.K_LEFT]:
                x = -SPEED
            if pressed_keys[pygame.K_RIGHT]:
                x = SPEED

            if pressed_keys[pygame.K_UP]:
                y = -SPEED
            if pressed_keys[pygame.K_DOWN]:
                y = SPEED
            if x != 0 and y != 0:
                x = x * (sqrt(2) / 2)
                y = y * (sqrt(2) / 2)
            self.rect.x += x
            self.rect.y += y
            if send:
                client.send(f"{id_client},{self.rect.x},{self.rect.y}".encode())


def recv_data(conn: socket.socket,all_sprites,id_user):
    while True:
        data = conn.recv(1024)
        if data == b"bye":
            break
        if data:
            print(list(map(int,data.decode().split(","))))
            id_conn,pox,posy = list(map(int,data.decode().split(",")))
            if id_conn != id_user:
                user = all_sprites[id_conn]
                user.rect.x = pox
                user.rect.y = posy
        else:
            break


# if are impostor set red else random color, and get id_
def main(client, id_user,room_size):
    pygame.init()
    signal.signal(signal.SIGINT, partial(signal_handler, client))
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGTH))
    all_sprites = []
    p1 = Player()
    for i in range(room_size):
        if i != id_user:
            all_sprites.append(Player())
        else:
            all_sprites.append(p1)

    threading.Thread(target=recv_data, args=(client,all_sprites,id_user)).start()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.send("DISCONNECT".encode())
                RUN = False
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))

        p1.move(client, id_user)

        for entity in all_sprites:
            window.blit(entity.surf, entity.rect)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((IP, PORT))
    except ConnectionRefusedError:
        print("Error, can't not connect")
        sys.exit(1)
    print("Waiting to server...")
    id_user,room_size = list(map(int,client.recv(5).decode().split(",")))
    main(client, id_user,room_size)
